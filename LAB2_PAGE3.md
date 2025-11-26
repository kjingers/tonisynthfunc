# Lab 2 Page 3: Exercise 3 - Implement and Test AI-Powered Assignment with GitHub Copilot

## Overview

Now that you are INTIMATELY FAMILIAR with the AI-powered REST/API specs and the functional spec you reviewed in Exercise 2 (the `ContosoSupport-AI-Assignment-Functional-Spec.md` GitHub based on the functional specification you implemented), you will implement the new `/assignsupportperson` HTTP/API implementation into the ContosoSupport REST API by using GitHub Copilot.

This exercise demonstrates the power of AI-assisted development and working with both specifications. Now we can code to understand and implement the functionality based on the technical specifications. Now that we edit the code, we can verify different UI/UX features and test with GitHub Copilot's prompt engineering, idea verification, and general draft testing features like auto-complete and hover explanations.

---

## Task 0: Getting Started

Prior to engaging GitHub Copilot to understand and implement the functionality based on the technical specifications, here are some tasks to get you up to speed on using GitHub Copilot in VS Code.

### Steps:

1. **If you are not familiar with GitHub Copilot** or if you have not used it for a while, review the Copilot documentation at [GitHub Copilot Documentation](https://docs.github.com/copilot)

2. **Verify Copilot is installed and configured** in Visual Studio Code
   - [ ] GitHub Copilot extension installed
   - [ ] Signed in to your GitHub account
   - [ ] Copilot icon visible in the status bar

3. **Completed the previous exercise and thoroughly understand the functional specification**
   - [ ] LAB2_PAGE2.md reviewed
   - [ ] ContosoSupport-AI-Assignment-Functional-Spec.md understood

4. **Access the starter code project and view the skeleton `assignsupportperson` method**
   - [ ] Starter code opened in VS Code
   - [ ] Located the assignsupportperson method placeholder

5. **GitHub Copilot available in your tenant Code**
   - [ ] Verified Copilot is active and working

---

## Task 1: Start a Copilot Chat to Understand the Code

Prior to diving directly into the implementation, start a new copilot chat and try to have the AI help you understand the existing ContosoSupport REST API service.

### Steps:

1. **Open the GitHub Copilot Chat** (side panel, new conversation or workspace chat)
   - [ ] Copilot Chat panel opened

2. **Start a conversation with GitHub Copilot** (ask about the current structure)
   - [ ] Ask: "Can you explain the architecture of this ContosoSupport REST API?"

3. **Have Copilot describe the components (ask about the current Azure setup and code structure)**
   - [ ] Understand the current service architecture
   - [ ] Identify key classes and methods
   - [ ] Review existing CRUD operations

4. **Ask specific questions about the codebase** (e.g., "How are tickets currently created?" or "What is the structure of the ticket object?")
   - [ ] Understanding of ticket creation flow
   - [ ] Ticket object structure documented

5. **Understand the existing API patterns (What's the get to CRUD endpoints?)**
   - [ ] GET endpoints reviewed
   - [ ] POST/PUT/DELETE patterns understood

6. **Inquire context about parameters (and + Azure AI Services)**
   - [ ] Azure AI integration points identified
   - [ ] Parameter passing patterns understood

---

## Task 2: Copilot-Guided Implementation

Use the functional specification document which found (ContosoSupport-AI-Assignment-Functional-Spec.md) to guide your prompt engineering with Copilot to implement the `assignsupportperson` function.

### Steps:

1. **Start a new Copilot conversation for implementation** (or continue your last)
   - [ ] New focused conversation started

2. **Provide the context to Copilot:**
   - [ ] Share key portions of the functional spec
   - [ ] Describe the endpoint: `POST /cases/{caseNumber}/assignsupportperson`
   - [ ] Explain the input (case number) and output (ticket + reasoning)

3. **Ask Copilot to draft the function signature and initial code**
   - [ ] Function signature generated
   - [ ] Basic structure in place

4. **Iteratively refine with Copilot:**
   - [ ] Implement the 4-factor weighted assignment algorithm
   - [ ] Add expertise matching logic (35% weight)
   - [ ] Add workload balance calculation (25% weight)
   - [ ] Add customer tier matching (20% weight)
   - [ ] Add availability/schedule checking (20% weight)

5. **Generate AI reasoning text**
   - [ ] Reasoning generation logic implemented
   - [ ] Transparent explanation of assignment decision

6. **Handle edge cases and error scenarios**
   - [ ] Case not found (404) handling
   - [ ] No suitable match found fallback
   - [ ] AI service unavailable (503) handling

7. **Review Copilot's suggested implementation for API Response:**
   - [ ] Response structure matches spec
   - [ ] Error responses properly formatted
   - [ ] HTTP status codes correct

---

## Task 3: Prompt Engineering and AI Logic

This Task 3 will highlight Copilot's skills and highlight the mechanics/logic for implementing/designing for AI as a value of the AI service.

### Prompt Generation Activities:

1. **Construct the AI prompt generation** in the implementation
   - [ ] System prompt defined for assignment logic
   - [ ] Context about ticket included in prompt
   - [ ] Support person data formatted for AI consumption

2. **Create structured input for AI reasoning:**
   - [ ] Ticket details (category, description, priority)
   - [ ] Available support persons with attributes
   - [ ] Weighting factors explained to AI

3. **Ask Copilot how to structure prompts for the API for responses (both responses)**
   - [ ] Response parsing logic implemented
   - [ ] Assignment extraction from AI response
   - [ ] Reasoning text extraction

4. **Use Copilot to help handle edge case (i.e., What happens if no one is available?)**
   - [ ] Fallback to team lead implemented
   - [ ] Round-robin logic for AI failure
   - [ ] Notification mechanism for escalations

5. **Prompt engineering considerations:**
   - [ ] Clear and specific instructions to AI
   - [ ] Structured output format requested
   - [ ] Examples provided in prompt if needed

---

## Task 4: Add Tests Plan for the Implementation

Using the testing and the sections/strategies from Exercise 2, let's testing with unit code. In this section, you're encouraged to collaborate with GitHub Copilot once you've implemented the feature, you will include a strategic approach of how to cover the edge cases of specifying the API.

### Testing Steps:

1. **Unit Test File Creation:**
   - [ ] Create test file for assignsupportperson
   - [ ] Set up test framework and imports

2. **Chat with Copilot for AI-generating test cases:**
   - [ ] Ask Copilot to generate test cases based on spec
   - [ ] Review suggested test scenarios

3. **Core Quality Review:**
   - [ ] Test successful assignment scenario
   - [ ] Test case not found (404)
   - [ ] Test no available support persons
   - [ ] Test AI service failure fallback

4. **Presentation Review:**
   - [ ] Test response structure validation
   - [ ] Test reasoning text presence
   - [ ] Test assignment field populated

5. **Performance Considerations:**
   - [ ] Response time < 5 seconds validation
   - [ ] Load testing considerations documented

6. **Ask Copilot additional questions (if applicable):**
   - [ ] Mock data generation for tests
   - [ ] Edge case coverage review

---

## Task 5: Code Quality and Documentation

Review the generated implementation and ensure code quality, readability, and documentation.

### Quality Steps:

1. **Validation Testing:**
   - [ ] Run unit tests and verify passing
   - [ ] Fix any failing tests

2. **Readability:**
   - [ ] Clear variable and function names
   - [ ] Proper code formatting
   - [ ] Logical code structure

3. **Logging:**
   - [ ] Assignment decisions logged
   - [ ] Error conditions logged
   - [ ] Performance metrics captured

4. **Comments:**
   - [ ] Complex logic explained with comments
   - [ ] Function documentation added
   - [ ] Parameter descriptions included

5. **Error Handling:**
   - [ ] Comprehensive try-catch blocks
   - [ ] Meaningful error messages
   - [ ] Proper HTTP status codes

6. **Documentation Review:**
   - [ ] API endpoint documented
   - [ ] Request/response examples provided
   - [ ] Error scenarios documented

---

## Task 6: Implementation Validation

Validate your implementation against all functional specification requirements from Exercise 2.

### Validation Checklist:

1. **FR-001: AI-powered assignment engine implemented**
   - [ ] Verified

2. **FR-002: Multiple factors considered** (expertise, workload, tier, availability)
   - [ ] All 4 factors implemented
   - [ ] Weighting applied correctly (35%, 25%, 20%, 20%)

3. **FR-003: REST endpoint `assignsupportperson` accepts case number**
   - [ ] Endpoint signature correct
   - [ ] Case number properly extracted from URL

4. **FR-004: Returns complete updated ticket with assigned alias**
   - [ ] Full ticket object returned
   - [ ] Assigned support person alias populated

5. **FR-005: AI reasoning provided**
   - [ ] Reasoning text generated
   - [ ] Reasoning explains assignment decision

6. **FR-009: Reassignment capability**
   - [ ] Can reassign if person already assigned
   - [ ] New reasoning generated on reassignment

7. **NFR-001: Performance < 5 seconds for 95% of requests**
   - [ ] Performance target documented
   - [ ] Optimization considerations noted

8. **NFR-002: Support 100 concurrent requests/minute**
   - [ ] Scalability considerations documented

9. **NFR-003: 99.9% uptime**
   - [ ] Error handling supports reliability
   - [ ] Fallback mechanisms in place

10. **API Specification Compliance:**
    - [ ] Request format matches spec
    - [ ] Response format matches spec
    - [ ] Error responses match spec (404, 503)

---

## Summary

In this exercise, you successfully collaborated with GitHub Copilot to implement the AI-powered support person assignment feature based on the functional requirements. You:

- Used Copilot Chat to understand the existing codebase
- Iteratively developed the assignment logic with AI assistance
- Implemented the 4-factor weighted assignment algorithm
- Created comprehensive tests with Copilot's help
- Validated the implementation against all functional requirements

This demonstrates how AI-powered development tools like GitHub Copilot can accelerate development while maintaining code quality and adherence to specifications.

---

## Next Steps

In the next exercise, you'll use the understanding of architecture requirements to deploy and test the implementation in a real Azure environment and measure its performance against the non-functional requirements.

---

## Completion Status

- [ ] Task 0: Getting Started - Copilot setup verified
- [ ] Task 1: Copilot Chat to understand code
- [ ] Task 2: Copilot-guided implementation complete
- [ ] Task 3: Prompt engineering and AI logic implemented
- [ ] Task 4: Tests created and passing
- [ ] Task 5: Code quality review complete
- [ ] Task 6: Implementation validated against spec
