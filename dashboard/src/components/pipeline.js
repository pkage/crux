import React from 'react'
import PipelineEditor from './pipeline_editor'
import '../styles/pipeline.css'

class PipelineContainer extends React.Component {
	
	render() {
		return (
			<div className="container is-fluid">
				<div className="level">
					<h1 className="is-size-2 level-left">Pipelines</h1>
					<div className="level-right align-baseline">
						<div className="field is-marginless">
							<p className="control has-icons-left">
								<input className="input" type="text" placeholder="Pipeline name" autoComplete="off"/>
								<span className="icon is-small is-left">
									<i className="fas fa-file"></i>
								</span>
							</p>
						</div>
						&nbsp;
						<div className="buttons has-addons">
							<a className="button">
								<span className="icon is-small">
									<i className="fas fa-upload"></i>
								</span>
								<span>Load</span>
							</a>
							<a className="button">
								<span className="icon is-small">
									<i className="fas fa-save"></i>
								</span>
								<span>Save</span>
							</a>
							<a className="button is-success is-selected">
								<span className="icon is-small">
									<i className="fas fa-play"></i>
								</span>
								<span>Run</span>
							</a>
						</div>
					</div>
				</div>
				<hr/>
				<PipelineEditor
					pipeline={this.props.pipeline}

					getPipelineDependencyCandidates={this.props.getPipelineDependencyCandidates}
					addPipelineDependency={this.props.addPipelineDependency}
					removePipelineDependency={this.props.removePipelineDependency}

					addPipelineStep={this.props.addPipelineStep}
					movePipelineStep={this.props.movePipelineStep}
					deletePipelineStep={this.props.deletePipelineStep}
					setPipelineParamValue={this.props.setPipelineParamValue}
					setPipelineStepRemap={this.props.setPipelineStepRemap}
					deletePipelineStepRemap={this.props.deletePipelineStepRemap}

					savePipeline={this.props.savePipeline}
					loadPipeline={this.props.loadPipeline}/>
			</div>
		)
	}
}

export default PipelineContainer

