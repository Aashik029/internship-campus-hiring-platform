import { Link } from "react-router-dom";

const STEPS = [
  {
    n: "1",
    title: "Students build a profile",
    text: "Add skills, browse open internships, apply in one click and track every application on a live status board.",
  },
  {
    n: "2",
    title: "Companies post roles",
    text: "Publish internships with required skills, review applicants and move them from Applied to Selected.",
  },
  {
    n: "3",
    title: "Admins keep it clean",
    text: "Oversee every user, post and application from one dashboard — with full moderation control.",
  },
];

export default function Home() {
  return (
    <div>
      <header className="hero mt-2">
        <div className="overline text-white-50 mb-2">Internship &amp; Campus Hiring</div>
        <h1 className="display-5 mb-3">
          Where students meet
          <br />
          their first opportunity.
        </h1>
        <p className="lead mb-4">
          Connect students looking for internships with companies that want to hire
          interns — profiles, posts, applications and status tracking in one place.
        </p>
        <div className="d-flex gap-2 flex-wrap">
          <Link to="/signup" className="btn btn-light btn-lg">
            Create free account
          </Link>
          <Link to="/login" className="btn btn-outline-light btn-lg">
            Login
          </Link>
        </div>
        <div className="hero-stats">
          <div>
            <strong>3 roles</strong>
            <span>Student · Company · Admin</span>
          </div>
          <div>
            <strong>5 stages</strong>
            <span>Applied → Selected pipeline</span>
          </div>
          <div>
            <strong>100%</strong>
            <span>Free for campuses</span>
          </div>
        </div>
      </header>

      <section className="mt-5">
        <div className="overline mb-1">How it works</div>
        <h2 className="page-title mb-4">Hiring in three steps</h2>
        <div className="row g-4">
          {STEPS.map((s) => (
            <div className="col-md-4" key={s.n}>
              <div className="card card-lift h-100">
                <div className="card-body p-4">
                  <div className="step-num">{s.n}</div>
                  <h5 className="fw-bold">{s.title}</h5>
                  <p className="text-muted mb-0">{s.text}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card mt-4">
        <div className="card-body p-4 d-flex flex-wrap align-items-center justify-content-between gap-3">
          <div>
            <h5 className="fw-bold mb-1">Ready to get hired — or to hire?</h5>
            <p className="text-muted mb-0">Join as a student or post your first internship today.</p>
          </div>
          <Link to="/signup" className="btn btn-primary btn-lg">
            Get started
          </Link>
        </div>
      </section>
    </div>
  );
}
