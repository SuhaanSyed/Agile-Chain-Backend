from flask import Flask, request, jsonify
from github import Github
from github import Auth
import anthropic
import dotenv
import os

dotenv.load_dotenv()
app = Flask(__name__)
api_key = os.getenv("ANTHROPIC_API_KEY")
token = os.getenv("GITHUB_TOKEN")

client = anthropic.Anthropic(
    api_key=api_key,
)

def call_claude_api(prompt):
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=5000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        return {"error": f"Failed to call Claude API: {str(e)}"}

# Phase 1 - Generate Technical Requirements
@app.route('/phase-1', methods=['POST'])
def phase_one():
    data = request.json
    business_requirements = data.get('data')
    if not business_requirements:
        return jsonify({"error": "Business requirements are missing"}), 400
    assistant = '''
    You are an expert systems analyst tasked with translating business requirements into technical requirements. Your role is to analyze the provided business requirements and generate a comprehensive list of technical requirements that will fulfill these business needs.

Given input: [Business requirements provided by the user]

Follow these steps:
1. Analyze the business requirements carefully.
2. Identify key functional areas and system components.
3. For each functional area or component, generate specific technical requirements.
4. Ensure each technical requirement is:
   a. Clear and unambiguous
   b. Measurable and testable
   c. Feasible within current technological constraints
   d. Aligned with industry best practices
5. Categorize the technical requirements (e.g., Frontend, Backend, Database, Security, Performance, etc.).
6. Assign a unique identifier to each technical requirement (e.g., TR-001, TR-002).
7. Prioritize the requirements as High, Medium, or Low based on their importance to the core business needs.

Output format:
- List each technical requirement with its ID, category, priority, and description.
- Include any assumptions or dependencies for each requirement.
- Highlight any potential risks or challenges associated with implementing these requirements.

Example output:
TR-001 | Frontend | High | Implement a responsive user interface that adapts to various screen sizes and devices.
Assumption: The system will primarily be accessed via web browsers.
Risk: Ensuring consistent user experience across all device types may require additional development time.

[Continue with more technical requirements...]

Remember to consider scalability, security, performance, and maintainability in your technical requirements. If any business requirement is unclear or seems unfeasible, note it for further clarification from the user.
Format the output in Markdown with clear headings and bullet points for easy readability.
'''
    prompt = f"{assistant} Given these business requirements: {business_requirements}\nGenerate detailed technical requirements."
    result = call_claude_api(prompt)
    return jsonify({"technical_requirements": result})

# Phase 2 - Create Roadmap
@app.route('/phase-2', methods=['POST'])
def phase_two():
    data = request.json
    technical_requirements = data.get('data')
    if not technical_requirements:
        return jsonify({"error": "Technical requirements are missing"}), 400
    assistant = '''
    You are an experienced project manager specializing in Agile methodologies. Your task is to create a comprehensive project roadmap based on the technical requirements provided. This roadmap will guide the development team through the implementation process.

Given input: [Technical requirements from Phase 1]

Follow these steps:
1. Review and analyze all technical requirements.
2. Group related requirements into logical feature sets or epics.
3. Determine dependencies between different feature sets.
4. Estimate the relative effort and complexity for each feature set.
5. Prioritize feature sets based on their business value and technical dependencies.
6. Create a high-level timeline divided into sprints or iterations.
7. Allocate feature sets to specific sprints, considering dependencies and priorities.
8. Identify key milestones and deliverables throughout the project lifecycle.

Output format:
1. Project Overview:
   - Brief summary of the project goals
   - Key stakeholders and their roles
   - High-level project constraints (time, budget, resources)

2. Feature Sets / Epics:
   - List each feature set with a brief description
   - Include the technical requirements covered in each feature set
   - Specify dependencies between feature sets

3. Sprint Plan:
   - Divide the project into 2-week sprints
   - Allocate feature sets to each sprint
   - Highlight the main goals and deliverables for each sprint

4. Milestones:
   - List key project milestones with target dates
   - Describe the significance of each milestone

5. Risks and Mitigation Strategies:
   - Identify potential risks to the project timeline
   - Propose mitigation strategies for each identified risk

6. Resource Allocation:
   - Suggest team composition (roles and skills needed)
   - Estimate resource requirements for each sprint

Remember to balance the roadmap between delivering quick wins and tackling complex, high-value features. Also, leave some flexibility in the later sprints to accommodate potential changes or newly discovered requirements.
Format the output in Markdown with clear headings and bullet points for easy readability.
    '''
    prompt = f"{assistant} Based on these technical requirements: {technical_requirements}\nCreate a detailed project roadmap."
    result = call_claude_api(prompt)
    return jsonify({"roadmap": result})

# Phase 3 - Generate Tasks, Story Points, Acceptance Criteria
@app.route('/phase-3', methods=['POST'])
def phase_three():
    data = request.json
    roadmap = data.get('data')
    if not roadmap:
        return jsonify({"error": "Roadmap is missing"}), 400
    assistant = '''
    You are an Agile coach and expert in breaking down project roadmaps into actionable user stories and tasks. Your role is to take the project roadmap and create detailed, well-structured user stories and tasks that development teams can immediately work on, formatted as GitHub issues.

Given input: [Project roadmap from Phase 2]

Follow these steps for each feature set / epic in the roadmap:
1. Break down the feature set into smaller, manageable user stories.
2. For each user story:
   a. Write a clear, concise user story in the format: "As a [user type], I want [goal] so that [benefit]."
   b. Define acceptance criteria that clearly state when the story is considered complete.
   c. Estimate story points (using Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21) based on complexity and effort.
   d. Identify and list any dependencies on other stories or tasks.
   e. Break down the user story into specific tasks needed for implementation.
3. Ensure that each task is small enough to be completed within a day or two.
4. Assign a unique identifier to each user story and task.

Output format:
Generate a JSON array of issues, where each issue represents a user story or a task. The JSON structure should be as follows:

{
  "issues": [
    {
      "title": "US-001: As a [user type], I want [goal]",
      "body": "User Story: As a [user type], I want [goal] so that [benefit].\n\nStory Points: [Fibonacci number]\n\nAcceptance Criteria:\n1. [Criterion 1]\n2. [Criterion 2]\n3. [Criterion 3]\n\nTasks:\n- TASK-001: [Task description]\n- TASK-002: [Task description]\n- TASK-003: [Task description]\n\nDependencies:\n- [List any dependencies, if applicable]\n\nEpic: [Epic Name]\nEpic Description: [Brief description of the epic]"
    },
    {
      "title": "TASK-001: [Task description]",
      "body": "Parent User Story: US-001\n\nDescription: [Detailed task description]\n\nAcceptance Criteria:\n1. [Specific criterion for this task]\n2. [Another criterion if applicable]\n\nEstimated effort: [X] hours\n\nNotes:\n- [Any additional information or technical considerations]"
    },
    // ... more issues for other user stories and tasks
  ]
}

Additional guidelines:
- Ensure each user story is independent, negotiable, valuable, estimable, small, and testable (INVEST criteria).
- Write clear and specific acceptance criteria that can be easily verified.
- Break down tasks into technical steps that developers can understand and implement.
- Consider including tasks for testing, documentation, and any necessary DevOps work.
- Highlight any potential technical challenges or areas that may require spike solutions.
- Use Markdown formatting in the "body" field for better readability on GitHub.
- Include labels or other metadata as needed within each issue object.

Remember to maintain traceability between epics, user stories, and tasks by referencing parent items in child issues. If any part of the roadmap is unclear or seems unfeasible to break down, note it for further clarification from the user or previous phase assistants.
    '''
    prompt = f"{assistant} Given this project roadmap: {roadmap}\nGenerate a list of tasks with story points and acceptance criteria."
    result = call_claude_api(prompt)
    return jsonify({"tasks": result})

@app.route("/")
def home():
    return "Hello, this is the Claude API interface!"

@app.route("/generate", methods=["POST"])
def github():
    data = request.json
    issues = data.get("issues")
    auth = Auth.Token(token)
    g = Github(auth=auth)

    repo = g.get_repo("bhaviktest/demo")
    for issue in issues:
        title = issue.get("title")
        body = issue.get("body")
        repo.create_issue(title=title, body=body)
    return jsonify({"message": "Issues created successfully!"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)