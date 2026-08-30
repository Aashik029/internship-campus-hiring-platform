import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Signup() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "student" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="row justify-content-center mt-3">
      <div className="col-md-6 col-lg-5">
        <div className="card">
          <div className="auth-band">
            <h4>Join CampusHire</h4>
            <p>Create your free student or company account.</p>
          </div>
          <div className="card-body p-4">
            {error && <div className="alert alert-danger py-2">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Full name</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.full_name}
                  onChange={update("full_name")}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={form.email}
                  onChange={update("email")}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Password (min 6 chars)</label>
                <input
                  type="password"
                  className="form-control"
                  value={form.password}
                  onChange={update("password")}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">I am a</label>
                <select className="form-select" value={form.role} onChange={update("role")}>
                  <option value="student">Student</option>
                  <option value="company">Company</option>
                </select>
              </div>
              <button className="btn btn-primary w-100" disabled={loading}>
                {loading ? "Creating..." : "Sign up"}
              </button>
            </form>
            <p className="text-muted small mt-3 mb-0">
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
