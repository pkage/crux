import React from 'react'

class DaemonsView extends React.Component {
	constructor(props) {
		super(props)

		this.state = {
			inp_address: (this.props.daemon_addr === null) ? 'tcp://localhost:30020' : ''
		}
	}

	connectDaemon() {
		this.props.connectDaemon(this.state.inp_address)
	}

	render () {
		const showDaemon = (addr) => {
			if (addr !== null) {
				return (
					<section className="hero is-success is-medium is-bold is-mobile">
						<article key={addr} className="hero-body">
							<div className="container is-mobile">
								<h1 className="title">{addr}</h1>
								<h2 className="subtitle">connected</h2>
							</div>
						</article>
					</section>
				)
			} else {
				return (
					<section className="hero is-warning is-medium is-bold is-mobile">
						<article key={addr} className="hero-body">
							<div className="container is-mobile">
								<h1 className="title">not connected</h1>
							</div>
						</article>
					</section>
				)
			}
		}
		return (
			<div>
				{showDaemon(this.props.daemon_addr)}
				<br/>
				<div className="level container is-fluid">
					<div className="level-left">
						<div className="control has-icons-left">
							<input
								className="input"
								placeholder="Address"
								value={this.state.inp_address}
								onChange={e => this.setState({inp_address: e.target.value})}
								onKeyUp={e => {if (e.keyCode === 13) this.connectDaemon()}}
							/>
							<span className="icon is-left">
								<i className="fas fa-plug"></i>
							</span>
						</div>&nbsp;
						<a className="button is-primary" onClick={() => this.connectDaemon()}>Connect</a>
					</div>
				</div>
			</div>
		)
	}
}

export default DaemonsView
