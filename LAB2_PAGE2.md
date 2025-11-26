# Lab 2 Page 2: Exercise 2 - Review Technical Specifications

## Overview

Understanding Foundry's functionality as it applies to the foundation of an assistant feature (Jetbot enhancement).

In this exercise, you will review the functional specification for the `contososupport-assistant` chatbot to gain a comprehensive understanding of the supported functionality. This is essential to design the most effective support representative AI chatbot that engages with customer inquiries, using data engineering, extraction, parsing, and retrieval attributes to deliver instant help support, provide product recommendations, answer product specifications, automate distribution, and enhance customer experience.

---

## Task 1: Prepare for Flow Functionality

**Objective:** Review the functional specification document to understand the implementation.

### Steps:

1. **Open the functional specification document:** `ContosoSupport-AI-Assignment-Functional-Spec.md`
   - [x] Document opened and reviewed
   - **Source:** https://onebranch.visualstudio.com/Bootcamp/_git/Labs (ContosoSupport-AI-Assignment-Functional-Spec.md)

2. **Review the execution statement and requirements** to understand:
   - [x] **Current system challenges identified:**
     - Manual assignment of support personnel to tickets
     - No intelligent routing based on complexity/subject matter
     - Potential delays during high-volume periods
     - Inconsistent assignment quality based on human judgment
   - [x] **Business driving context:** Improve efficiency and customer experience through AI-powered assignment
   - [x] **Proposed solution:** New REST endpoint `assignsupportperson` that uses AI to assign optimal support person

3. **Analyze the core functional requirements:**
   - [x] **New API Endpoint:** `POST /cases/{caseNumber}/assignsupportperson`
   - [x] **Input:** Case number only (simple interface)
   - [x] **Output:** Complete updated ticket with assigned support person alias + AI reasoning
   - [x] **Key Features:**
     - Automatic reassignment if person already assigned
     - AI reasoning transparency for audit/understanding
     - Backward compatibility with existing ticket structure

4. **Understand the AI Assignment Logic (Section 5)**
   - [x] **Weighting factors identified:**
     - Expertise Matching: 35% (skills, resolution rate, certifications)
     - Workload Balance: 25% (active tickets, complexity, productivity)
     - Customer Tier Matching: 20% (authorization level, SLA requirements)
     - Availability and Schedule: 20% (online status, timezone, response time)
   - [x] **Fallback mechanisms:** Round-robin assignment if AI fails, escalation to team lead if no match

5. **Performance and Non-Functional Requirements:**
   - [x] **Response time:** < 5 seconds for 95% of requests
   - [x] **Throughput:** Support 100 concurrent requests per minute
   - [x] **Availability:** 99.9% uptime SLA
   - [x] **Security:** AI reasoning logged for audit purposes

6. **Integration Requirements (Section 6):**
   - [x] **Database changes:**
     - New table: `ai_assignment_log` (track decisions and reasoning)
     - Modified table: `support_cases` (add AI assignment fields)
   - [x] **External dependencies:**
     - Cloud-based ML assignment engine
     - Real-time model inference
     - Monitoring and logging infrastructure

7. **Error Handling and Edge Cases:**
   - [x] **Case not found:** Return HTTP 404 with error details
   - [x] **AI service unavailable:** Return HTTP 503 with retry guidance
   - [x] **No suitable match:** Escalate to team lead with notification

8. **Discussion Questions:**
   - [x] **What is the assignment endpoint structure?**
     - Answer: `POST /cases/{caseNumber}/assignsupportperson` - simple input (case number only)
   
   - [x] **What information is returned in the response?**
     - Answer: Complete ticket object + assignedsupportpersonalias + assignmentReasoning
   
   - [x] **How does the system handle reassignment?**
     - Answer: If person already assigned, system assigns a new person and returns updated ticket with new reasoning

   - [x] **What are the key testing requirements?**
     - Answer: Unit testing (logic validation), Integration testing (end-to-end workflow), Performance testing (load/response time), UAT (assignment quality validation)

---

## Task 2: Data Standardization Flows

**Objective:** Review the API request/response structure and AI assignment factors.

### API Request/Response Analysis:

1. **Request Structure**
   - [x] **Endpoint:** `POST /cases/{caseNumber}/assignsupportperson`
   - [x] **Required:** Case number in URL path
   - [x] **Optional body parameters:** requestId, priority (HIGH/MEDIUM/LOW), notes
   - [x] **Headers:** Content-Type: application/json, Accept: application/json

2. **Response Structure (Success - HTTP 200)**
   - [x] Complete ticket object with fields:
     - id, title, isComplete, owner, description
     - **assignedsupportpersonalias** (newly assigned)
     - **assignmentReasoning** (AI explanation)

3. **Error Handling Patterns**
   - [x] **404 - Case Not Found:** Returns error code + message
   - [x] **503 - AI Service Unavailable:** Returns error + retry guidance + timestamp

### AI Assignment Factors (from Section 5.1):

- [x] **Expertise Matching (35% weight)**
  - Technical skill alignment with ticket category
  - Historical resolution success rate
  - Certifications and training
  - Subject matter expertise depth

- [x] **Workload Balance (25% weight)**
  - Current active ticket count
  - Complexity of existing assignments
  - Estimated time to completion
  - Historical productivity metrics

- [x] **Customer Tier Matching (20% weight)**
  - Authorization level for customer tier
  - Experience with high-value accounts
  - SLA requirements
  - Escalation capabilities

- [x] **Availability and Schedule (20% weight)**
  - Current online status
  - Time zone alignment
  - Scheduled availability windows
  - Response time history

---

## Task 3: Data Requirements

**Objective:** Understand data needed for AI assignment decisions.

### Data Sources Required:

1. **Support Ticket Data**
   - [x] Case number, title, description
   - [x] Category and complexity level
   - [x] Customer priority/tier level
   - [x] Current assignment status

2. **Support Person Data**
   - [x] Expertise and skill profiles
   - [x] Historical resolution rates by category
   - [x] Certifications and training records
   - [x] Current workload (active tickets, complexity)
   - [x] Availability status and schedule
   - [x] Time zone information
   - [x] Authorization levels

3. **Historical Performance Data**
   - [x] Resolution success rates
   - [x] Response time metrics
   - [x] Customer satisfaction scores
   - [x] Productivity metrics

4. **Database Requirements (Section 6.1)**
   - [x] **New table:** `ai_assignment_log` - stores all AI decisions and reasoning
   - [x] **Modified table:** `support_cases` - adds AI assignment fields and reasoning reference

---

## Task 4: Integration Topics

**Objective:** Review architecture and integration patterns.

### Integration Components (Section 6.2):

1. **AI/ML Service Integration**
   - [x] Cloud-based machine learning assignment engine
   - [x] Real-time model inference capabilities
   - [x] Training data pipeline for continuous improvement

2. **Database Operations**
   - [x] **Insert:** Log assignment decisions to `ai_assignment_log`
   - [x] **Update:** Modify `support_cases` with assigned person and reasoning
   - [x] Transaction integrity for multi-table updates

3. **Monitoring and Logging**
   - [x] Assignment decision audit trail (for compliance)
   - [x] Performance metrics collection (response time, success rate)
   - [x] Error tracking and alerting
   - [x] AI reasoning logged for transparency

4. **Fallback Mechanisms (Section 5.2)**
   - [x] **AI service failure:** Round-robin assignment to available support persons
   - [x] **No suitable match:** Assign to team lead with escalation flag
   - [x] **Notification:** Alert support management of failures/escalations

---

## Task 5: Quality and Testing Considerations

**Objective:** Understand testing strategy from Section 7.

### Testing Requirements:

1. **Unit Testing (Section 7.1)**
   - [x] AI assignment logic validation
   - [x] Edge case handling:
     - No available support persons
     - System overload scenarios
     - Invalid case numbers
   - [x] Response format validation (JSON structure)

2. **Integration Testing (Section 7.2)**
   - [x] End-to-end assignment workflow testing
   - [x] Database transaction integrity verification
   - [x] External AI service integration testing
   - [x] Fallback mechanism validation

3. **Performance Testing (Section 7.3)**
   - [x] Load testing: 100 concurrent requests/minute
   - [x] Response time validation: < 5 seconds for 95% requests
   - [x] AI service timeout and fallback testing
   - [x] Stress testing under high-volume conditions

4. **User Acceptance Testing (Section 7.4)**
   - [x] Assignment quality validation by support managers
   - [x] Customer satisfaction impact measurement
   - [x] Support person workload distribution analysis
   - [x] AI reasoning transparency and usefulness review

### Quality Metrics:

- [x] **Accuracy:** Assignment quality and appropriateness
- [x] **Performance:** Response time < 5 seconds
- [x] **Reliability:** 99.9% uptime SLA
- [x] **Transparency:** Clear AI reasoning for audit/understanding
- [x] **Fairness:** Balanced workload distribution

---

## Summary

In this first exercise, you conducted a thorough analysis of the functional specification for the AI-powered support person assignment feature. By examining the business requirements, technical approaches, service and platform, AI logic, and implementation considerations, the foundation will be set as you deploy the implementation phase in the next section.

---

## Key Deliverables

- [ ] Reviewed the full functional specification document
- [ ] Understood the core functional and requirement requirements
- [ ] Reviewed the AI assignment logic and weighting factors
- [ ] Examined the technical components that need to be implemented
- [ ] Identified quality and testing considerations

---

## Next Steps

In the next exercise, you'll use the understanding of architecture requirements to collaborate with your GitHub Copilot to implement the `contososupport-assistant` method.

---

## Completion Checklist

- [x] Task 1: Reviewed functional specification document
- [x] Task 2: Understood API structure and AI assignment factors  
- [x] Task 3: Documented data requirements
- [x] Task 4: Reviewed integration architecture and components
- [x] Task 5: Analyzed testing strategy and quality metrics
- [x] Summary discussion completed

### Key Implementation Insights:

**API Design:**
- Simple interface: case number in → complete ticket + reasoning out
- Stateless operation with optional request parameters
- Clear error handling with HTTP status codes

**AI Assignment Engine:**
- 4-factor weighted decision model (Expertise 35%, Workload 25%, Customer Tier 20%, Availability 20%)
- Fallback mechanisms for resilience
- Transparent reasoning for audit and trust

**Technical Architecture:**
- REST endpoint integrated with existing ContosoSupport service
- Cloud-based ML service for real-time inference
- Database changes: new log table + modified cases table
- Comprehensive monitoring and logging

**Success Criteria:**
- Performance: < 5 sec response, 100 req/min throughput
- Reliability: 99.9% uptime
- Quality: Improved assignment accuracy and customer satisfaction
- Transparency: AI reasoning logged and provided in response
