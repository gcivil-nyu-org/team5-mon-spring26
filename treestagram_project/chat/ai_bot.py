# import random

# class MockAIGenerator:
#     @staticmethod
#     def generate_response(tree, message):
#         """
#         Parses the user's message and contextually injects tree data
#         into a simulated AI response.
#         """
#         msg_lower = message.lower()

#         # Context extraction from the tree instance
#         species = getattr(tree, 'spc_common', '') or "a mystery tree"
#         health = getattr(tree, 'health', '') or "unknown"
#         status = getattr(tree, 'status', '') or "standing here"
#         problems = getattr(tree, 'problems', '') or "none that I know of"
#         dbh = getattr(tree, 'tree_dbh', '') or "unknown"

#         # Keyword triggers
#         if "health" in msg_lower or "sick" in msg_lower:
#             return f"As a {species}, my health is currently rated as '{health}'. Issues? Well, I have: {problems}."
#         elif "species" in msg_lower or "what are you" in msg_lower or "kind" in msg_lower:
#             return f"I am a {species}! We are quite common in this neck of the woods."
#         elif "size" in msg_lower or "big" in msg_lower or "tall" in msg_lower or "dbh" in msg_lower:
#             return f"My Trunk Diameter (DBH) is {dbh} inches. I've been growing for a while!"
#         elif "hello" in msg_lower or "hi" in msg_lower:
#             return f"Hello there! I'm your friendly neighborhood {species}. What would you like to know about me?"
#         elif "problem" in msg_lower or "issue" in msg_lower:
#             if problems.lower() == "none" or not problems:
#                 return "I'm doing great! No reported problems."
#             else:
#                 return f"I do have some issues... specifically: {problems}. Please take care of me!"
#         else:
#             responses = [
#                 f"I'm just a {species} enjoying the sunshine. Did you know my health is {health}?",
#                 f"Photosynthesis is hard work! Need anything else?",
#                 f"As a {status} tree, I don't have many opinions on that. But I can tell you my DBH is {dbh} inches!",
#                 f"Interesting question... but I'm just a tree! Try asking me about my health, species, or size."
#             ]
#             return random.choice(responses)
