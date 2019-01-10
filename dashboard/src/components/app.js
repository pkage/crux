import React from 'react'
import { Route, BrowserRouter as Router } from 'react-router-dom'
import { fromJS } from 'immutable'
import swal from 'sweetalert2'

import Navigation from './nav'
import DaemonsView from './daemon'
import ComponentsView from './components'
import PipelineContainer from './pipeline'
import ExecutionView from './execution'

import CruxAPIClient from '../api'

class App extends React.Component {
	constructor(props) {
		super(props)
		this.api = new CruxAPIClient(this.props.apiurl)
		window.app = this

		// immutable api mirror
		this.state = {
			crux: fromJS({
				components: this.api.components,
				apiurl: this.api.apiurl,
				daemon_addr: this.api.daemon_addr,
				pipeline: this.api.pipeline,
			})
		}
		this.api.onStateChange((key, value) => {
			let prevState = this.state.crux
			this.setState({crux: prevState.set(key, value)})
		})
		this.api.get_daemon()
			.then(addr => {
				if (addr !== null) {
					return this.api.get_components()
				}
			})
			.catch(this.catchError)
	}
	render() {
		return (
			<Router>
				<div>
					<Route path='/' component={Navigation}/>
					<Route path='/daemons' component={() => (
						<DaemonsView
							daemon_addr={this.state.crux.get('daemon_addr')}
							connectDaemon={(addr) => this.connectDaemon(addr)}/>
					)}/>
					<Route path='/components' component={() => (
						<ComponentsView
							components={this.state.crux.get('components')}
							refreshComponents={() => this.getComponents()}
							sendToComponent={(addr, payload) => this.sendToComponent(addr, payload)}/>
					)}/>
					<Route path='/pipelines' component={() => (
						<PipelineContainer
							pipeline={this.state.crux.get('pipeline')}
							getPipelineDependencyCandidates={         () => this.getPipelineDependencyCandidates()}
							addPipelineDependency={ (name, src, version) => this.addPipelineDependency(name, src, version)}
							removePipelineDependency={              name => this.removePipelineDependency(name)}
							addPipelineStep={					    name => this.addPipelineStep(name)}
							movePipelineStep={ 			 (index, offset) => this.movePipelineStep(index, offset)}
							deletePipelineStep={				   index => this.deletePipelineStep(index)}
							setPipelineParamValue={(index, param, value) => this.setPipelineParamValue(index, param, value)}
							setPipelineStepRemap={	  (index, src, dest) => this.setPipelineStepRemap(index, src, dest)}
							deletePipelineStepRemap={		(index, src) => this.deletePipelineStepRemap(index, src)}
							savePipeline={							  () => this.savePipeline()}
							loadPipeline={							  pl => this.loadPipeline(pl)}/>
					)}/>
					<Route path='/execution' component={ExecutionView}/>
					
				</div>
			</Router>
		);
	}

	catchError(error) {
		swal({
			type: 'error',
			title: 'Backend error occurred',
			html: `<code>${error.message}</code>`
		})
	}

	getComponents() {
		this.api.get_components()
			.catch(this.catchError)
	}

	connectDaemon(addr) {
		this.api.connect_daemon(addr)
			.then(() => this.api.get_daemon())
			.then(() => this.api.get_components())
			.catch(this.catchError)
	}

	async sendToComponent(addr, payload) {
		return await this.api.send_to_component(addr, payload)
			.catch(this.catchError)
	}

	// pipeline methods
	getPipelineDependencyCandidates() {
		return this.api.get_pipeline_dependency_candidates()
	}

	addPipelineDependency(name, src, version) {
		return this.api.add_pipeline_dependency(name, src, version)
	}

	removePipelineDependency(name) {
		return this.api.remove_pipeline_dependency(name)
	}

	addPipelineStep(name) {
		return this.api.add_pipeline_step(name)
	}

	movePipelineStep(index, offset) {
		return this.api.move_pipeline_step(index, offset)
	}

	deletePipelineStep(index) {
		return this.api.delete_pipeline_step(index)
	}

	setPipelineParamValue(index, param, value) {
		return this.api.set_pipeline_param_value(index, param, value)
	}

	setPipelineStepRemap(index, src, dest) {
		return this.api.set_pipeline_step_remap(index, src, dest)
	}

	deletePipelineStepRemap(index, src) {
		return this.api.delete_pipeline_step_remap(index, src)
	}

	savePipeline() {
		return this.api.save_pipeline()
	}

	loadPipeline(pl) {
		return this.api.load_pipeline(pl)
	}

}

export default App;
