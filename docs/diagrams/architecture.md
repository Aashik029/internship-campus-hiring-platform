# Architecture Diagram (as-built, Review-II)

```mermaid
flowchart TB
    subgraph Client["Client Layer (Vercel)"]
        Browser["React SPA (Vite)\nStudent / Company / Admin dashboards"]
        Swagger["Swagger UI / Thunder Client"]
    end

    subgraph API["API Layer - FastAPI (/api/v1, Render)"]
        AuthRouter["Auth Router\n/auth"]
        StudentRouter["Student Router\n/students"]
        CompanyRouter["Company Router\n/companies"]
        AdminRouter["Admin Router\n/admin"]
        HealthRouter["Health Router\n/health"]
    end

    subgraph Core["Core"]
        Deps["deps.py\nJWT auth + role guards"]
        Security["security.py\nbcrypt + JWT"]
        Config["config.py\npydantic-settings / .env"]
    end

    subgraph Service["Service Layer - Business Logic"]
        AuthService["auth.py\nlogging: signup/login"]
        StudentService["students.py"]
        CompanyService["companies.py\nSMTP status emails"]
        AdminService["admin.py\noverview + manage deletes"]
        EmailService["email.py\nno-op when SMTP unset"]
    end

    subgraph Data["Data Layer"]
        Models["SQLAlchemy Models\n8 tables"]
        InitDB["init_db.py\ncreate_all + admin seed"]
        DB[("Cloud PostgreSQL (prod)\nSQLite fallback (dev)")]
    end

    CI["GitHub Actions CI\nlint + pytest + deploy hooks"]

    Browser --> AuthRouter
    Browser --> StudentRouter
    Browser --> CompanyRouter
    Browser --> AdminRouter
    Swagger --> AuthRouter
    Swagger --> StudentRouter
    Swagger --> CompanyRouter
    Swagger --> AdminRouter

    AuthRouter --> Deps
    StudentRouter --> Deps
    CompanyRouter --> Deps
    AdminRouter --> Deps
    HealthRouter --> Config

    Deps --> Security
    Security --> Config

    AuthRouter --> AuthService
    StudentRouter --> StudentService
    CompanyRouter --> CompanyService
    AdminRouter --> AdminService
    CompanyService --> EmailService

    AuthService --> Models
    StudentService --> Models
    CompanyService --> Models
    AdminService --> Models

    Models --> DB
    InitDB --> Models
    InitDB --> DB

    AuthService --> CI
    StudentService --> CI
    CompanyService --> CI
    AdminService --> CI
```

![Architecture Diagram](architecture.png)
