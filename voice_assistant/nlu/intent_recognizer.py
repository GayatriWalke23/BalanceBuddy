"""Intent recognition for voice commands using a simple rule-based approach."""
import re
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import parsedatetime

@dataclass
class Intent:
    """Represents a recognized intent with extracted parameters."""
    name: str
    confidence: float
    params: Dict[str, str]

class IntentRecognizer:
    def __init__(self):
        self.cal = parsedatetime.Calendar()
        
        # Define intent patterns
        self.intent_patterns = {
            "add_task": [
                r"add (?:a )?task(?: to)?(?: do)? (.+)",
                r"create (?:a )?task(?: to)? (.+)",
                r"remind me to (.+)",
            ],
            "list_tasks": [
                r"(?:show|list|what are)(?: my)? tasks",
                r"what do i need to do",
                r"show my to[- ]do list",
            ],
            "set_reminder": [
                r"remind me (?:to )?(.+?) (?:at|on|in) (.+)",
                r"set (?:a )?reminder (?:to )?(.+?) (?:at|on|in) (.+)",
            ],
            "delete_task": [
                r"(?:delete|remove|complete) task (.+)",
                r"mark task (.+)(?: as)? (?:done|complete|finished)",
            ],
            "help": [
                r"(?:what can you|help|how do you) do",
                r"what (?:commands|things) can i say",
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in self.intent_patterns.items()
        }

    def recognize(self, text: str) -> Optional[Intent]:
        """Recognize intent from text input.
        
        Args:
            text: Input text to recognize intent from
            
        Returns:
            Intent object if recognized, None otherwise
        """
        text = text.lower().strip()
        
        # Try each intent pattern
        for intent_name, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.match(text)
                if match:
                    params = {}
                    
                    # Extract parameters based on intent
                    if intent_name == "add_task":
                        params["task_description"] = match.group(1)
                        
                    elif intent_name == "set_reminder":
                        params["task_description"] = match.group(1)
                        time_str = match.group(2)
                        parsed_time = self._parse_time(time_str)
                        if parsed_time:
                            params["reminder_time"] = parsed_time.isoformat()
                        
                    elif intent_name == "delete_task":
                        params["task_id"] = match.group(1)
                    
                    return Intent(
                        name=intent_name,
                        confidence=0.9,  # Fixed for rule-based
                        params=params
                    )
        
        return None
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string into datetime object."""
        try:
            # Use parsedatetime to handle natural language time expressions
            struct_time, parse_status = self.cal.parse(time_str)
            if parse_status > 0:
                return datetime(*struct_time[:6])
        except Exception as e:
            print(f"Error parsing time: {e}")
        return None

    def get_example_commands(self) -> Dict[str, List[str]]:
        """Get example commands for each intent."""
        examples = {
            "add_task": [
                "add task buy groceries",
                "create task call mom",
                "remind me to take medicine"
            ],
            "list_tasks": [
                "show my tasks",
                "what do I need to do",
                "list tasks"
            ],
            "set_reminder": [
                "remind me to call John at 3pm",
                "set reminder to take medicine in 2 hours",
                "remind me to check email at 9am tomorrow"
            ],
            "delete_task": [
                "delete task 1",
                "mark task 2 as done",
                "complete task buy groceries"
            ],
            "help": [
                "what can you do",
                "help",
                "what commands can I say"
            ]
        }
        return examples
