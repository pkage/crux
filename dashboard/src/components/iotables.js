import React from 'react'

const createIORows = (desc) => {
	// functional? idk this was fun
	return Object.keys(desc).sort().map(key => (
		<tr key={key}>
			<td className="monospace">{key}</td>
			<td><i>{desc[key].type}</i></td>
		</tr>
	))
}

const createIOTable = (desc, name) => {
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
						createIORows(desc) : 
						<tr>
							<td colSpan="2"><i>No {name}s.</i></td>
						</tr>
				}
			</tbody>
		</table>
	)
}

const createInputTable = (desc) => createIOTable(desc, 'input')
const createOutputTable = (desc) => createIOTable(desc, 'output')

const createParamTable = (params) => {
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

export {createInputTable, createOutputTable, createParamTable}
