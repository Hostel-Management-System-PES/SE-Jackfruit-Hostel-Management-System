# Hostel Management System

## Overview

The Hostel Management System is a web-based application developed as part of the
Software Engineering course at PES University.

The system is designed to manage student information, hostel room allocation,
fee records, complaints, and leave requests for a single hostel.

## Scope

The system has two user roles:

- **Student** – manages their profile, views room and fee details, submits complaints
  and leave requests.
- **Admin** – manages student accounts, rooms, room allocation, fee records,
  complaints, and leave requests.

### Out of Scope

- Warden role
- Visitor management
- Room-change request workflow
- Online payment gateway
- Receipt/PDF generation
- Multi-hostel management

## Project Status

**Phase 1 – Requirements Analysis**

Currently, the team is working on the Software Requirements Specification (SRS).
Implementation and testing will be carried out in later phases.

## Documentation

- [Software Requirements Specification](docs/SRS.md)

## Team

| Member | SRN | Responsibility |
|---|---|---|
| Vilohith | SRN | Student & Access Management |
| Prathiksha | PES1UG24CS925 | Room & Allocation Management |
| Tejasvi K S | PES1UG24CS499 | Fee Management |
| Varsha | SRN | Complaints & Leave Management |

## Technology

**To be finalized by the team.**

The project will use Python-based web development as specified by the course
requirements.

## Development Workflow

The team follows a Git-based workflow using feature branches and Pull Requests.

- `main` – stable shared branch
- Individual branches – feature/section development
- Pull Requests – review and merge changes into `main`
