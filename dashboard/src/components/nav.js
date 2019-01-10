import React from 'react'
import { Link } from 'react-router-dom'

class Navigation extends React.Component {
	constructor(props) {
		super(props)

		this.state = {
			navOpen: false
		}
	}

	toggleNav() {
		this.setState({navOpen: !this.state.navOpen})
	}
	render() {
		const is_selected = (name) => {
			if ('/' + name.toLowerCase() === window.location.pathname) {
				return (
					<div className="navbar-item"><span>{name}</span></div>
				)
			}
			return <div className="navbar-item"><Link to={name.toLowerCase()}>{name}</Link></div>
		}
		return (
			<nav className="navbar">
				<div className="navbar-brand">
					<div className="navbar-item">
						<strong className="is-size-4">Crux</strong>
					</div>
					<a
						onClick={() => this.toggleNav()}
						className={`navbar-burger ${this.state.navOpen ? 'is-active' : ''}`}>
						<span></span>
						<span></span>
						<span></span>
					</a>	
				</div>
				<div className={`navbar-menu ${this.state.navOpen ? 'is-active' : ''}`}>
					<div className="navbar-end">
						{is_selected('Daemons')}
						{is_selected('Components')}
						{is_selected('Pipelines')}
						{is_selected('Execution')}
					</div>
				</div>
			</nav>
		)
	}
}

export default Navigation
