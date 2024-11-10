import "./App.css";
// importing components from react-router-dom package
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

// import Home component
import Home from "./pages/home";
// import About component
import Calendar from "./pages/calendar";
// import ContactUs component
import Settings from "./pages/settings";
// import ContactUs component
import Assignments from "./pages/assignments";

export default function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/assignments" element={<Assignments />} />
          <Route path="*" element={<Navigate to="/" />}
          />
        </Routes>
      </Router>
    </>
  );
}

