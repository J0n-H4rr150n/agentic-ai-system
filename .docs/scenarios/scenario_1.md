1. i need to define a 'system prompt' for a specific 'llm' to use.

2. start (should be changed to just 'string' input) - target url is one node, and initial user prompt is another node.

3. allowed tools (tool nodes - like browser tool) need to be 'available' to the llm during its looping.

4. start a loop/steps with the llm node

5. inside the loop, the llm review the target url and initial prompt to come up with an initial plan of action. in the llm's outputs it will have a response, llm_decision, llm_findings, llm_notes, llm_critique, llm_confidence, llm_next_steps, llm_action, etc... (all the things we might need to keep track of its decisions, findings, etc.)

6. if a tool is 'high risk' or, the llm confidence is less than 0.5 (or some other threshold), then there should be a 'tool'/action for the llm to pause the loop and ask for human input.

7. etc..
