import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Summary from './Summary.jsx'



createRoot(document.getElementById('root')).render(
  <StrictMode>
	<Summary />
  </StrictMode>,
)