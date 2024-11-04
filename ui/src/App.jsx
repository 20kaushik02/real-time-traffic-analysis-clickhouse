import './App.css'
import Header from './components/Header/Header'
import LineChart from './components/LineChart/LineChart'

function App() {
  return (
    <>
      <Header />
      <div className='row'>
        <LineChart
          name={"Packets"}
          data={[
            { x: 1324508400000, y: 34 },
            { x: 1324594800000, y: 54 },
            { x: 1326236400000, y: 43 },
          ]}
          xaxis={{ type: "datetime" }}
          ytitle={"Packets"}
        />
      </div>
    </>
  )
}

export default App
