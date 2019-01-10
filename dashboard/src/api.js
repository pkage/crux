class CruxAPIClient {
	_stateHandlers = []
	apiurl = null
	components = {}
	daemon_addr = null
	pipeline = {components: {}, pipeline: []}

	/**
	 * Create an API client, pointing at the specified API url
	 * @param apiurl the current API url
	 */
	constructor(apiurl) {
		this.apiurl = apiurl
		this.init_pipeline()
		// todo: put something here
	}

	/* --- HELPERS --- */

	/**
	 * Helper function to encode query parameters
	 * @param obj dict of query key/values
	 * @return &-joined URI string
	 */
	encodeURIs(obj) {
		// map over object, convert uri, and join with '&'
		let components = []
		for (let key in obj) {
			components.push(`${key}=${window.encodeURIComponent(obj[key])}`)
		}
		return components.join('&')
	}

	/**
	 * Set the internal state of the API, notifying the appropriate dispatcher
	 * @param key key to change
	 * @param value value to set
	 */
	_setState(key, value) {
		this[key] = value
		for (let handler of this._stateHandlers) {
			handler(key, value)
		}
	}

	onStateChange(handler) {
		this._stateHandlers.push(handler)
	}

	/* --- DAEMON METHODS --- */

	/**
	 * Connect to a daemon (async)
	 * @param addr address (relative to API machine)
	 * @return Promise (fulfill when connected)
	 */
	async connect_daemon(addr) {
		const ret = await fetch(`${this.apiurl}/daemon/connect?${this.encodeURIs({daemon: addr})}`)
			.then(r => r.json())
		if (!ret.success) {
			throw new Error(ret.message)
		}
		return true
	}

	/**
	 * Get the currently connected daemon
	 * @return Promise (fulfill with daemon address)
	 */
	async get_daemon() {
		const ret = await fetch(`${this.apiurl}/daemon/get`)
			.then(r => r.json())

		this._setState('daemon_addr', ret.address)
		return ret.address
	}

	/* --- COMPONENT METHODS --- */

	/**
	 * (Re-)load components from server
	 *
	 * also mirrors to this.components for sync access
	 *
	 * @return promise (fulfill when component list is resolved)
	 */
	async get_components() {
		const response = await fetch(`${this.apiurl}/components/list`)
			.then(r => r.json())

		// throw an error
		if (!response.success) {
			throw new Error(response.message)
		}

		this._setState('components', response.components)

		return response.components
	}

	/**
	 * Get a specific running component by address
	 * @param address the address to use
	 * @return promise with cruxfile
	 */
	async get_component(address) {
		const call = this.encodeURIs({address})
		const response = await fetch(`${this.apiurl}/components/get?${call}`)
			.then(r => r.json)

		if (!response.success) {
			throw new Error(response.message)
		}

		return response.component
	}

	/**
	 * Get any (loaded) component's address by name
	 * @param name name of component
	 * @return component object or null
	 */
	get_component_addr(name) {
		for (let key in this.components) {
			if (this.components[key].name === name) {
				return key
			}
		}
		return null
	}

	/**
	 * Load a component from a path
	 * @param path (relative to daemon address)
	 * @return promise (with address)
	 */
	async load_component(path) {
		const call = this.encodeURIs({path})
		const response = await fetch(`${this.apiurl}/components/load?${call}`)
			.then(r => r.json())

		if (!response.success) {
			throw new Error(response.message)
		}

		return response.address
	}

	/**
	 * Send an arbitrary message to a component
	 * @param addr the address to use
	 * @param message message to send (containing a name)
	 * @return result of computation
	 */
	async send_to_component(address, message) {
		// basic sanity check
		if (!('name' in message)) {
			throw new Error('message must contain a "name"!')
		}

		const call = this.encodeURIs({address})

		// make the call
		const response = await fetch(`${this.apiurl}/components/send?${call}`, {
			body: JSON.stringify(message),
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		}).then(r => r.json())

		if (!response.success) {
			throw new Error(response.message)
		}

		return response.response
	}

	/* --- PIPELINE METHODS --- */

	/**
	 * Initialize the pipeline
	 */
	init_pipeline() {
		this._setState('pipeline', {components: {}, pipeline: []})
	}

	/**
	 * Get list of candidates (list of names)
	 * @return list of names
	 */
	get_pipeline_dependency_candidates() {
		// get unique names
		return [...new Set(Object.keys(this.components).map(k => this.components[k].name))]
	}

	/**
	 * Register a component as a dependency of the pipeline
	 *
	 * Note: if src & version are null, this will attempt to resolve from a loaded pipeline
	 *
	 * @param name name of component
	 * @param src component source
	 * @param version component version target
	 */
	add_pipeline_dependency(name, src, version) {
		const caddr = this.get_component_addr(name)
		const reg = {}

		if (caddr === null) {
			let component = this.components[caddr]
			if (version === null) {
				reg.version = component.version
			}
			if (src === null) {
				reg.src = caddr
			}
		}

		let pline = this.pipeline
		pline.components[name] = reg

		this._setState('pipeline', pline)
	}

	/**
	 * Remove a dependency by name
	 * @param name name to remove
	 */
	remove_pipeline_dependency(name) {
		if (name in this.pipeline.components) {
			delete this.pipeline.components[name]

			// remove each dependent step by pushing an inclusion range to reorder_pipeline_steps
			const keep = []
			for (let idx in this.pipeline.pipeline) {
				if (this.pipeline.pipeline[idx].component !== name) {
					keep.push(+idx)
				}
			}
			this.reorder_pipeline_steps(keep)
			this._setState('pipeline', this.pipeline)
		}
	}

	
	/**
	 * Add a component to the pipeline
	 * @param name component name
	 */
	add_pipeline_step(name) {
		let addr = this.get_component_addr(name)

		if (addr === null) {
			throw new Error(`could not find component '${name}'`)
		}

		let cobj = this.components[addr]

		// init with defaults
		const params = JSON.parse(JSON.stringify(cobj.parameters))
		for (let key in params) {
			if ('default' in params[key]) {
				params[key].value = params[key].default
			}
		}

		this.pipeline.pipeline.push({
			component: name,
			parameters: params,
			remap: {}
		})
		this._setState('pipeline', this.pipeline)
	}
	
	/**
	 * Reorder pipeline
	 * @param new_order sequential array 0-(len-1) of new ordering
	 */
	reorder_pipeline_steps(new_order) {
		let pline = []
		for (let el of new_order) {
			pline.push(this.pipeline.pipeline[el])
		}
		this.pipeline.pipeline = pline
		this._setState('pipeline', this.pipeline)
	}

	/**
	 * Move pipeline step
	 * @param index index of original step
	 * @param offset offset from original position
	 */
	move_pipeline_step(index, offset) {
		const dest = (+index + +offset)
		// bounds check
		if (dest < 0 || dest >= this.pipeline.pipeline.length) return;
		// hacky create a range quickly
		const range = [...Array(+this.pipeline.pipeline.length).keys()]

		let swap = range[dest]
		range[dest] = range[+index]
		range[+index] = swap

		this.reorder_pipeline_steps(range)
	}

	/**
	 * Delete a step from a pipeline
	 * @param index index of the step
	 */
	delete_pipeline_step(index) { 
		if (+index < 0 || +index >= this.pipeline.pipeline.length) return;
		
		// hacky create a range quickly
		const range = [...Array(+this.pipeline.pipeline.length).keys()]
		range.splice(+index, 1)

		this.reorder_pipeline_steps(range)

	}

	/**
	 * Set pipeline param value
	 * @param index index of step
	 * @param param parameter to set
	 * @param value value to set
	 */
	set_pipeline_param_value(index, param, value) {
		this.pipeline.pipeline[index].parameters[param].value = value
		this._setState('pipeline', this.pipeline)
	}

	/**
	 * Add a remap to a step
	 * @param index to set at
	 * @param src source field
	 * @param dest destination mapping
	 */
	set_pipeline_step_remap(index, src, dest) {
		if (+index < 0 || +index >= this.pipeline.pipeline.length) return;

		this.pipeline.pipeline[+index].remap[src] = dest

		this._setState('pipeline', this.pipeline)
	}

	/**
	 * Remove remapping from a pipeline step
	 * @param index to remove from
	 * @param src source field
	 */
	delete_pipeline_step_remap(index, src) {
		if (+index < 0 || +index >= this.pipeline.pipeline.length) return;

		if (src in this.pipeline.pipeline[+index].remap) {
			delete this.pipeline.pipeline[+index].remap[src]
		}

		this._setState('pipeline', this.pipeline)
	}

	/**
	 * Set a pipeline remap
	 * @param index index to replace at
	 * @param obj remap object
	 */
	set_pipeline_remap(index, obj) {
		this.pipeline.pipeline[index].remap = obj
		this._setState('pipeline', this.pipeline)
	}
	
	/**
	 * Save pipeline
	 * @returns JSON representation of pipeline
	 */
	save_pipeline() {
		return JSON.stringify({sorry: 'not yet implemented'})
	}

	/**
	 * Load pipeline
	 * @param pipeline to load (object or str)
	 */
	load_pipeline(pl) {
		console.log('pipeline to load: ')
		console.log(pl)
	}
}

export default CruxAPIClient
