import React from 'react'
import {Link} from 'react-router-dom'
import {TextParameter, BooleanParameter, DropdownParameter} from './parameters'

const PipelineEditorElementRemap = props => {

	return (
		<p> remapping </p>
	)
}

const PipelineEditorElement = props => {
	const createParameter = (name) => {
		const param = props.step.parameters[name]
		const upd = val => props.setParameter(name, val)
		let inp = <p key={name}> unsupported param "{param.type}"</p>
		if (param.type === 'dropdown') {
			inp = (
				<DropdownParameter
					key={name}
					update={upd}
					name={name}
					field={param}
					value={param.value}/>
			)
		} else if (param.type === 'text') {
			inp = (
				<TextParameter
					key={name}
					update={upd}
					value={param.value}
					field={param}/>
			)
		} else if (param.type === 'boolean') {
			inp = (
				<BooleanParameter
					key={name}
					update={upd}
					value={param.value}
					field={param}/>
			)
		}
		return inp
	}

	let parameters = []
	for (let key in props.step.parameters) {
		parameters.push(createParameter(key))
	}


	return (
		<div className="pipeline-row">
			<div className="pipeline-row-left">
				<div className="pipeline-row-left-border-top"></div>
				<div className="pipeline-row-left-border-bottom"></div>
				<div className="pipeline-row-left-ball"></div>
			</div>
			<div className="pipeline-row-right">
				<div className="level is-mobile">
					<div className="level-left toolbar-parent">
						<b className="is-size-3">{props.step.component}&nbsp;</b>

						<div className="toolbar">
							<span className="icon" onClick={() => props.movePipelineStep(props.index, 1)}>
								<i className="fas fa-lg fa-angle-down icon-button has-text-info"></i>
							</span>
							<span className="icon" onClick={() => props.movePipelineStep(props.index, -1)}>
								<i className="fas fa-lg fa-angle-up icon-button has-text-info"></i>
							</span>
							<span className="icon" onClick={() => props.deletePipelineStep(props.index)}>
								<i className="fas fa-lg fa-times icon-button has-text-danger"></i>
							</span>
						</div>
					</div>
				</div>
				{parameters}
				<PipelineEditorElementRemap/>
				<br/>
			</div>
		</div>
	)
}

const PipelineEditorPalette = props => (
	<div className="dropdown is-hoverable">
		<div className="dropdown-trigger clickable is-size-3 has-text-grey-lighter">
			<b>add &nbsp;</b>
			<span className="icon is-small">
				<i className="fas fa-angle-down"></i>
			</span>
		</div>
		<div className="dropdown-menu">
			<div className="dropdown-content">
				{Object.keys(props.candidates).map(el => (
					<a
						className="dropdown-item"
						key={el}
						onClick={() => props.addCandidate(el)}>
						{el}
					</a>
				))}
				{ (Object.keys(props.candidates).length !== 0) && <hr className="dropdown-divider"/> }
				<div className="dropdown-item">
					<p>You can add more components from the <b>Dependencies</b> section.</p>
				</div>
			</div>
		</div>
		<br/>
	</div>
)

class PipelineDependencyList extends React.Component {
	renderComponent(name) {
		const component = this.props.components[name]
		return (
			<div className="pipeline-component box" key={name} >
				<div className="level is-marginless is-mobile">
					<b className="level-left">{name}</b>

					<span className="level-right">
						<span
							className="icon is-small icon-button has-text-danger"
							onClick={() => this.props.removePipelineDependency(name)}>
							<i className="fas fa-times"></i>
						</span>
					</span>
				</div>
				<div className="level is-marginless">
					<div className="level-left">
						<span>version:&nbsp;</span>
						<code>{component.version || '>=0.0.0'}</code>
					</div>
				</div>
			</div>
		)
	}
	renderComponentSelector() {
		const candidates = this.props.candidates.map(name => (
			<a
				className="dropdown-item"
				key={name}
				onClick={() => this.props.addPipelineDependency(name)}>
				{name}
			</a>
		))
		return (
			<div className="dropdown is-hoverable pipeline-component pipeline-component-tentative">
				<div className="dropdown-trigger clickable is-size-3 has-text-grey-lighter">
					<span className="icon is-small">
						<i className="fas fa-plus"></i>
					</span>
				</div>
				<div className="dropdown-menu">
					<div className="dropdown-content">
						{ candidates }
						{ (candidates.length !== 0) && <hr className="dropdown-divider"/> }
						<div className="dropdown-item">
							<p>You can load more components from the <Link to="daemons">daemons</Link> page.</p>
						</div>
					</div>
				</div>
			</div>
		)
	}
	render() {
		const components = []
		for (let c in this.props.components) {
			components.push(this.renderComponent(c))
		}

		return (
			<div className="column">
					<div className="is-size-3"> Dependencies </div>
					<br/>
					<div className="pipeline-component-container">
						{components}
						{this.renderComponentSelector()}
					</div>
			</div>
		)
	}
}

class PipelineEditor extends React.Component {
	render() {
		return (
			<div className="columns">
				<PipelineDependencyList
					components={this.props.pipeline.components}
					candidates={this.props.getPipelineDependencyCandidates()}
					addPipelineDependency={this.props.addPipelineDependency}
					removePipelineDependency={this.props.removePipelineDependency}/>
				<div className="column is-two-thirds">
					<div className="is-size-3"> Processing steps </div>
					<br/>
					{this.renderPipeline()}
				</div>
			</div>
		)
	}

	renderPipeline() {
		let pl = []
		// do it this way so we have a unique key
		for (let idx in this.props.pipeline.pipeline) {
			pl.push(
				<PipelineEditorElement
					key={idx}
					index={idx}
					setParameter={(param, value) => this.props.setPipelineParamValue(idx, param, value)}
					movePipelineStep={this.props.movePipelineStep}
					deletePipelineStep={this.props.deletePipelineStep}
					step={this.props.pipeline.pipeline[idx]}/>
			)
		}

		return (
			<div className="pipeline-container pipeline-container-has-tentative">
				{pl}
				<div className="pipeline-row">
					<div className="pipeline-row-left">
						<div className="pipeline-row-left-border-top"></div>
						<div className="pipeline-row-left-border-bottom"></div>
						<div className="pipeline-row-left-ball"></div>
					</div>
					<div className="pipeline-row-right">
						<PipelineEditorPalette
							addCandidate={name => this.props.addPipelineStep(name)}
							candidates={this.props.pipeline.components || {}}/>
					</div>
				</div>
			</div>
		)
	}
}

export default PipelineEditor
