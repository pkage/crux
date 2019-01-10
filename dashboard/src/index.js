import React from 'react'
import ReactDOM from 'react-dom'
import App from './components/app'
import 'bulma/css/bulma.css'
//import 'font-awesome/css/font-awesome.css'
import './styles/index.css'

const APIURL = 'http://127.0.0.1:8080/api'
ReactDOM.render(
	<App apiurl={APIURL}/>,
	document.getElementById('root')
)
