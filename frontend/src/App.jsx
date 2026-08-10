import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ListPage from "./pages/ListPage";
import "./App.css";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/list/:listId" element={<ListPage />} />
    </Routes>
  );
}
