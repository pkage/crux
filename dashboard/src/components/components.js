import React from 'react'

import ComponentListView from './component'

class ComponentsView extends React.Component {
	constructor(props) {
		super(props)
		this.state = {filter: ''}
	}

	render() {
		const components = []
		for (let addr in this.props.components) {
			let name = (this.props.components[addr].name + ' ' + addr).toLowerCase()
			if ( name.indexOf(this.state.filter.toLowerCase()) === -1) continue;
			components.push(
				<ComponentListView
					key={addr}
					addr={addr}
					component={this.props.components[addr]}
					shutdownComponent={() => {
						this.props.sendToComponent(addr, {name: 'shutdown'})
							.then(() => this.props.refreshComponents())
					}}/>)
		}

		return (
			<div className="container is-fluid">
				<div className="level is-mobile">
					<h1 className="is-size-2 level-left">Components</h1>
					<div className="level-right align-baseline">
						<div className="field is-marginless">
							<p className="control has-icons-left">
								<input className="input" type="text" placeholder="Filter..." autoComplete="off" onKeyUp={(e) => this.setState({filter: e.target.value})}/>
								<span className="icon is-small is-left">
									<i className="fas fa-search"></i>
								</span>
							</p>
						</div>
						&nbsp;
						<a className="button is-success" onClick={this.props.refreshComponents}>
							<span className="icon is-small">
								<i className="fas fa-sync"></i>
							</span>
							<span>Refresh</span>
						</a>
					</div>
				</div>
				<hr/>
				{components}
				<br/>
			</div>
		)
	}
}

export default ComponentsView
