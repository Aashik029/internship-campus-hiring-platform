const COMPANIES = [
  { name: "Acme Corp", initials: "AC", color: "primary" },
  { name: "Globex", initials: "GX", color: "success" },
  { name: "Initech", initials: "IN", color: "info" },
  { name: "Hooli", initials: "HL", color: "warning" },
  { name: "Umbrella Tech", initials: "UT", color: "danger" },
  { name: "Stark Industries", initials: "SI", color: "secondary" },
];

export default function TrustedCompanies() {
  return (
    <div className="mt-5 pt-4 border-top">
      <h2 className="mb-2">Trusted by leading companies</h2>
      <p className="text-muted mb-4">
        Top firms post internships on our platform and find the right talent faster.
      </p>
      <div className="row g-4">
        {COMPANIES.map((company) => (
          <div className="col-6 col-lg-2 col-md-4" key={company.name}>
            <div className="text-center">
              <div
                className={`bg-${company.color} text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-2`}
                style={{ width: "72px", height: "72px", fontSize: "1.5rem", fontWeight: "bold" }}
              >
                {company.initials}
              </div>
              <div className="fw-semibold">{company.name}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}