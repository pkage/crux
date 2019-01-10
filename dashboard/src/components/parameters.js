import React from 'react'

class TextParameter extends React.Component {
	constructor(props) {
		super(props)

		this.state = {
			expanded: false
		}
	}

	toggleExpanded() {
		this.setState({
			expanded: !this.state.expanded
		})
	}

	render() {
		return (
			<div className="field">
				<label className="label">{this.props.field.name}</label>
				<div className="control">
					{this.state.expanded ? 
							<textarea
								className="textarea"
								placeholder="Text input"
								defaultValue={this.props.value || ""}
								onBlur={e => this.props.update(e.target.value)}>
							</textarea> :
							<input
								className="input"
								type="text"
								placeholder="Text input"
								defaultValue={this.props.value || ""}
								onBlur={e => this.props.update(e.target.value)}/>
					}
				</div>
				<a onClick={() => this.toggleExpanded()}>
					{this.state.expanded ?
						'collapse field' :
						'expand field'
					}
				</a>
			</div>
		)
	}
}

const BooleanParameter = props => (
	<div className="field">
		<div className="control">
			<label className="checkbox">
				<input
					type="checkbox"
					checked={props.value}
					onChange={e => props.update(e.target.checked)}/>
				&nbsp;{props.field.name}
			</label>
		</div>
	</div>
)

const DropdownParameter = props => (
	<div className="field">
		<label className="label">{props.field.name}</label>
		<div className="control">
			<div className="select">
				<select defaultValue={props.value || "__DISABLED"} onChange={e => props.update(e.target.value)}>
					<option value="__DISABLED" disabled="disabled">select...</option>
					{props.field.options.map(opt => (
						<option key={opt} value={opt}>{opt}</option>		
					))}
				</select>
			</div>
		</div>
	</div>
)


class ParameterForm extends React.Component {
	constructor(props) {
		super(props)

		this.state = {form: {}}
	}

	createField(key, field) {
		let paramdata = {
			update: value => {
				let copy = Object.assign({}, this.state.form)
				copy[key] = value
				this.setState({form: copy}, () => {
					this.props.onUpdate(this.state.form)
				})
			},
			key: key,
			...field
		}
		if (field.type.toLowerCase() === "boolean") {
			return BooleanParameter(paramdata)
		} else if (field.type.toLowerCase() === "text") {
			// gross...
			return (
				<TextParameter
					update={paramdata.update}
					key={paramdata.key}
					field={field}>
				</TextParameter>
			)
		} else if (field.type.toLowerCase() === "dropdown") {
			return DropdownParameter(paramdata)
		}
	}

	render() {

		let fields = []
		for (let key in this.props.parameters) {
			fields.push(this.createField(key, this.props.parameters[key]))
		}
		
		return (
			<div>
				{fields}
			</div>
		)
	}
}

export { DropdownParameter, TextParameter, BooleanParameter}
export default ParameterForm
