import { useEffect, useState } from "react";
import api from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function AdminDashboard() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [applications, setApplications] = useState([]);
  const [message, setMessage] = useState("");

  async function loadAll() {
    try {
      const [u, p, a] = await Promise.all([
        api.get("/admin/users"),
        api.get("/admin/posts"),
        api.get("/admin/applications"),
      ]);
      setUsers(Array.isArray(u.data) ? u.data : []);
      setPosts(Array.isArray(p.data) ? p.data : []);
      setApplications(Array.isArray(a.data) ? a.data : []);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not load admin data.");
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function removePost(id) {
    if (!window.confirm("Delete this post and its applications?")) return;
    try {
      await api.delete(`/admin/posts/${id}`);
      setMessage("Post deleted.");
      loadAll();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not delete post.");
    }
  }

  async function removeUser(id) {
    if (!window.confirm("Delete this user and their data?")) return;
    try {
      await api.delete(`/admin/users/${id}`);
      setMessage("User deleted.");
      loadAll();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not delete user.");
    }
  }

  return (
    <div>
      <h2 className="page-title">Welcome, {user.full_name}</h2>
      <p className="text-muted">
        Platform overview at a glance — moderate users, posts and applications.
      </p>
      {message && <div className="alert alert-info py-2">{message}</div>}

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-num">{users.length}</div>
              <div className="stat-label">Users</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-2 card">
            <div className="card-body">
              <div className="stat-num">{posts.length}</div>
              <div className="stat-label">Posts</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-3 card">
            <div className="card-body">
              <div className="stat-num">{applications.length}</div>
              <div className="stat-label">Applications</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-6">
          <div className="section-head">
            <h5 className="mb-0 fw-bold">Users</h5>
          </div>
          {users.length === 0 && <div className="empty-state">No users found.</div>}
          <ul className="list-group mb-4">
            {users.map((u) => (
              <li
                className="list-group-item d-flex justify-content-between align-items-center"
                key={u.id}
              >
                <div>
                  <strong>{u.full_name}</strong> — {u.email}{" "}
                  <span
                    className={`badge ms-1 ${
                      u.role === "admin"
                        ? "bg-danger"
                        : u.role === "company"
                          ? "bg-primary"
                          : "bg-success"
                    }`}
                  >
                    {u.role}
                  </span>
                </div>
                <button
                  className="btn btn-sm btn-outline-danger"
                  disabled={u.id === user.id}
                  title={u.id === user.id ? "You cannot delete yourself" : "Delete user"}
                  onClick={() => removeUser(u.id)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>

          <div className="section-head mt-4">
            <h5 className="mb-0 fw-bold">Internship posts</h5>
          </div>
          {posts.length === 0 && <div className="empty-state">No posts found.</div>}
          <ul className="list-group">
            {posts.map((p) => (
              <li
                className="list-group-item d-flex justify-content-between align-items-center"
                key={p.id}
              >
                <div>
                  <strong>{p.title}</strong>{" "}
                  <span
                    className={`badge ${p.is_open ? "bg-success" : "bg-secondary"} ms-1`}
                  >
                    {p.is_open ? "open" : "closed"}
                  </span>
                </div>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => removePost(p.id)}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-lg-6">
          <div className="section-head">
            <h5 className="mb-0 fw-bold">Applications</h5>
          </div>
          {applications.length === 0 && (
            <div className="empty-state">No applications yet.</div>
          )}
          <ul className="list-group">
            {applications.map((a) => (
              <li className="list-group-item" key={a.id}>
                <div>
                  <strong>{a.post_title}</strong> — {a.student_email}
                </div>
                <span className="badge bg-info text-dark">{a.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
