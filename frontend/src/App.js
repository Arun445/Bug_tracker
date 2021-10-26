import { BrowserRouter as Router, Route } from "react-router-dom";
import DashBoard from "./screens/DashBoard";
import NavBar from "./components/NavBar";
import SideBar from "./components/SideBar";
function App() {
  return (
    <Router>
      <NavBar />
      <SideBar />
      <main>
        <Route path="/" component={DashBoard} exact />
      </main>
    </Router>
  );
}

export default App;
