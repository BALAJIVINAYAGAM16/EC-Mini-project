import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CreateTask from "./pages/CreateTask";
import EditTask from "./pages/Edittask";
import ProtectedRoute from "./components/ProtectedRoute";
import Users from "./pages/Users";
import KanbanBoard from "./components/KanbanBoard";
import ApprovalPanel from "./components/ApprovalPanel";
import Documents from "./pages/Documents";
import AuditLog from "./pages/AuditLog";
import Notifications from "./pages/Notifications";
import AIInsights from "./pages/AIInsights";
import Billing from "./pages/Billing";
import Plans from "./pages/Plans";
import Organization from "./pages/Organization";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/create"
          element={
            <ProtectedRoute>
              <CreateTask />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit/:id"
          element={
            <ProtectedRoute>
              <EditTask />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/users" element={
  <ProtectedRoute>
    <Users />
  </ProtectedRoute>
} />
        <Route
          path="/kanban"
          element={
            <ProtectedRoute>
              <KanbanBoard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/approvals"
          element={
            <ProtectedRoute>
              <ApprovalPanel />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Documents />
            </ProtectedRoute>
          }
        />
        <Route
          path="/audit-logs"
          element={
            <ProtectedRoute>
              <AuditLog />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-insights"
          element={
            <ProtectedRoute>
              <AIInsights />
            </ProtectedRoute>
          }
        />
        <Route path="/billing" element={<Billing />} />
        <Route path="/plans" element={<Plans />} />
        <Route path="/organization" element={<Organization />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
