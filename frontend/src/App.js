import { BrowserRouter as Router, Route } from "react-router-dom";
import DashBoard from "./screens/DashBoard";
import NavBar from "./components/NavBar";
function App() {
  return (
    <Router>
      <NavBar />
      <main>
        <Route path="/" component={DashBoard} exact />
      </main>
    </Router>
  );
}

export default App;
