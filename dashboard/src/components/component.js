import React from 'react'
import swal from 'sweetalert2'
import {createParamTable, createInputTable, createOutputTable} from './iotables'

class ComponentListView extends React.Component {
	constructor(props) {
		super(props)
		this.state = {
			open: false,
			showCruxfile: false
		}
	}

	toggleDropdown() {
		this.setState({
			open: !this.state.open
		})
	}

	toggleCruxfile() {
		this.setState({
			showCruxfile: !this.state.showCruxfile
		})
	}

	shutdownComponent() {
		swal({
			title: 'Are you sure?',
			html: `Shut down component <b>${this.props.component.name}</b> running at <span class="monospace">${this.props.addr}</span>?`,
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: 'hsl(348, 100%, 61%)',
			confirmButtonText: 'Shut down',
			focusConfirm: false
		}).then(result => {
			if (!result.value) return; 
			this.props.shutdownComponent()
			swal({
				title: 'Sent shutdown message!',
				type: 'success'
			})
		})
	}

	createIORows(desc) {
		// functional? idk this was fun
		return Object.keys(desc).sort().map(key => (
			<tr key={key}>
				<td className="monospace">{key}</td>
				<td><i>{desc[key].type}</i></td>
			</tr>
		))
	}

	createIOTable(desc, name) {
		return (
			<table className="table">
				<thead>
					<tr>
						<th>{ name[0].toUpperCase() + name.slice(1).toLowerCase() }</th>
						<th>Type</th>
					</tr>
				</thead>
				<tbody>
					{(Object.keys(desc).length > 0) ?
							this.createIORows(desc) : 
							<tr>
								<td colSpan="2"><i>No {name}s.</i></td>
							</tr>
					}
				</tbody>
			</table>
		)
	}

	createParamTable(params) {
		const createParamRows = (params) => Object.keys(params).map(key => (
			<tr key={key}>
				<td className="monospace">{key}</td>
				<td>{params[key].name || ''}</td>
				<td>{params[key].type}</td>
			</tr>
		))

		return (
			<table className="table">
				<thead>
					<tr>
						<th>Parameter</th>
						<th>Description</th>
						<th>Type</th>
					</tr>
				</thead>
				<tbody>
					{(Object.keys(params).length > 0) ?
						createParamRows(params) :
						<tr>
							<td colSpan="3"><i>No parameters.</i></td>
						</tr>
					}
				</tbody>
			</table>
		)
	}

	render() {
		return (
			<div>
				<div className="level is-mobile">
					<div className="level-left is-size-4">
						<b>{this.props.component.name}</b>
						&nbsp;
						<span>({this.props.addr})</span>
					</div>
					<div className="level-right">
						<span className="icon" onClick={() => this.toggleDropdown()}>
							{(this.state.open === true) ?
									<i className="fas fa-angle-up has-text-primary icon-button"></i> :
									<i className="fas fa-angle-down has-text-primary icon-button"></i>
							}
						</span>
					</div>
				</div>
				{this.state.open &&
					<div>
						<div className="columns is-mobile">
							<div className="column">
								<b>author: </b> {this.props.component.author}<br/>
								<b>version: </b> {this.props.component.version}<br/>
								<b>description: </b> {this.props.component.description}<br/>
								<hr/>
								<a className="button is-danger" onClick={() => this.shutdownComponent()}>
									<span className="icon is-small">
										<i className="fas fa-power-off"></i>
									</span>
									<span>shutdown</span>
								</a>
							</div>
							<div className="column is-two-thirds">
								<div className="columns">
									<div className="column is-narrow">
										{createInputTable(this.props.component.inputs)}
									</div>
									<div className="column is-narrow">
										{createOutputTable(this.props.component.outputs)}
									</div>
									<div className="column">
										{createParamTable(this.props.component.parameters)}
									</div>
								</div>

								{ this.state.showCruxfile && 
									<pre>{JSON.stringify(this.props.component, null, 4)}</pre>
								}
								<a onClick={() => this.toggleCruxfile()}>
									{this.state.showCruxfile ? 'hide' : 'show'} cruxfile
								</a>
							</div>
						</div>
						<br/>
					</div>
				}
			</div>
		)
	}
}

export default ComponentListView
