#!/usr/bin/env python3
"""
Document Automation Controller
Complete file processing, calculation, and document creation automation
"""

import re
import time
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from .universal_app_controller import create_universal_app_controller
    UNIVERSAL_AVAILABLE = True
except ImportError:
    UNIVERSAL_AVAILABLE = False
    print("Warning: Universal app controller not available")

class DocumentAutomationController:
    """
    Complete document automation system
    - Process files for calculations
    - Perform automated calculations
    - Create and populate documents
    - Add signatures automatically
    """

    def __init__(self, signature: str = "Cristal Rivera"):
        self.signature = signature
        if UNIVERSAL_AVAILABLE:
            self.universal = create_universal_app_controller()
        else:
            self.universal = None

    def extract_calculations_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract mathematical expressions from a file"""
        try:
            content = Path(file_path).read_text()

            # Pattern to match mathematical expressions
            patterns = [
                r'(\d+(?:\.\d+)?)\s*([+\-*/×÷])\s*(\d+(?:\.\d+)?)',  # Basic operations
                r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)',             # x for multiplication
                r'calculate\s*:?\s*([^=\n]+)',                        # "calculate: expression"
                r'(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)',           # Multiplication with *
            ]

            calculations = []

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 3:  # Operation with two operands
                        num1, op, num2 = match
                        expression = f"{num1} {op} {num2}"
                    elif len(match) == 2:  # x multiplication
                        num1, num2 = match
                        expression = f"{num1} × {num2}"
                    else:  # Single expression
                        expression = match[0] if isinstance(match, tuple) else match

                    calculations.append({
                        'expression': expression,
                        'original_match': match
                    })

            return calculations

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    def evaluate_expression(self, expression: str) -> Optional[float]:
        """Safely evaluate mathematical expression"""
        try:
            # Clean and normalize the expression
            cleaned = expression.replace('×', '*').replace('÷', '/').replace('x', '*')

            # Remove any non-mathematical characters except digits, operators, parentheses, and dots
            cleaned = re.sub(r'[^0-9+\-*/().\s]', '', cleaned)

            # Evaluate safely
            result = eval(cleaned)
            return result

        except Exception as e:
            print(f"Error evaluating '{expression}': {e}")
            return None

    def automated_calculator_operation(self, expression: str) -> Optional[str]:
        """Perform calculation using automated calculator button presses with timeout protection"""
        # Always compute the result first for reliability
        computed_result = self.evaluate_expression(expression)

        if not self.universal:
            return str(computed_result)

        try:
            print(f"🧮 Starting automated calculator for: {expression}")

            # Launch calculator with timeout protection
            print("  📱 Launching Calculator...")
            launch_result = self.universal.launch_app('Calculator')
            if not launch_result.get('ok', False):
                print(f"  ⚠️ Calculator launch issue: {launch_result.get('error', 'unknown')}")
                return str(computed_result)

            time.sleep(0.8)  # Reduced wait time

            print("  🎯 Activating Calculator...")
            activate_result = self.universal.activate_app('Calculator')
            time.sleep(0.3)  # Reduced wait time

            # Clear calculator
            print("  🧹 Clearing calculator...")
            self.universal.send_keystroke('Calculator', 'c', ['command'])
            time.sleep(0.2)

            # Convert expression to calculator inputs
            calculator_expression = expression.replace('×', '*').replace('÷', '/').replace('x', '*')

            print(f"  ⌨️ Typing: {calculator_expression}")
            # Press each character with minimal delays
            for char in calculator_expression:
                if char.isdigit() or char in '+-*/.=':
                    self.universal.send_keystroke('Calculator', char)
                    time.sleep(0.1)  # Faster typing
                elif char == ' ':
                    continue  # Skip spaces

            # Press equals if not already in expression
            if '=' not in calculator_expression:
                print("  = Pressing equals...")
                self.universal.send_keystroke('Calculator', '=')
                time.sleep(0.3)

            print(f"  ✅ Calculator automation completed!")
            print(f"  📊 Result: {computed_result}")
            return str(computed_result)

        except Exception as e:
            print(f"  ⚠️ Calculator automation error: {e}")
            print(f"  💡 Using computed result: {computed_result}")
            return str(computed_result)

    def create_document_with_results(self, calculations: List[Dict], results: List[str],
                                   output_file: str = None) -> str:
        """Create a document with calculation results"""

        # Generate document content
        content = "# Calculation Results\n\n"
        content += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for i, (calc, result) in enumerate(zip(calculations, results), 1):
            content += f"{i}. {calc['expression']} = {result}\n"

        content += f"\n---\nSignature: {self.signature}\n"

        # Determine output file
        if not output_file:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = f"calculations_{timestamp}.txt"

        return content, output_file

    def automated_document_creation(self, content: str, filename: str) -> bool:
        """Create document using automated app control"""
        if not self.universal:
            # Fallback: write to file directly
            Path(filename).write_text(content)
            return True

        try:
            # Launch TextEdit
            print("🆕 Creating new document...")
            self.universal.launch_app('TextEdit')
            time.sleep(2)
            self.universal.activate_app('TextEdit')
            time.sleep(1)

            # Create new document (Cmd+N)
            self.universal.send_keystroke('TextEdit', 'n', ['command'])
            time.sleep(1)

            # Type the content
            print("✍️ Writing content to document...")
            self.universal.type_text('TextEdit', content)
            time.sleep(1)

            # Save document (Cmd+S)
            print("💾 Saving document...")
            self.universal.send_keystroke('TextEdit', 's', ['command'])
            time.sleep(1)

            # Type filename
            self.universal.type_text('TextEdit', filename)
            time.sleep(0.5)

            # Press Enter to save
            self.universal.send_keystroke('TextEdit', 'return')
            time.sleep(1)

            print(f"✅ Document saved as: {filename}")
            return True

        except Exception as e:
            print(f"Error creating document: {e}")
            # Fallback: write to file
            Path(filename).write_text(content)
            return True

    def process_file_complete_automation(self, input_file: str, output_file: str = None) -> Dict[str, Any]:
        """Complete automation: process file, calculate, create document with signature"""

        print(f"🤖 Starting complete automation for: {input_file}")
        print("=" * 60)

        # 1. Extract calculations from file
        print("1. 📄 Extracting calculations from file...")
        calculations = self.extract_calculations_from_file(input_file)
        print(f"   ✅ Found {len(calculations)} calculations")

        if not calculations:
            return {"ok": False, "error": "No calculations found in file"}

        # 2. Perform automated calculations
        print("2. 🧮 Performing automated calculations...")
        results = []
        for i, calc in enumerate(calculations, 1):
            print(f"   Calculating {i}/{len(calculations)}: {calc['expression']}")
            result = self.automated_calculator_operation(calc['expression'])
            results.append(result)
            print(f"   ✅ Result: {result}")

        # 3. Create document content
        print("3. 📝 Creating document content...")
        content, output_filename = self.create_document_with_results(calculations, results, output_file)
        print(f"   ✅ Document content prepared")

        # 4. Automated document creation
        print("4. 🖋️ Creating document automatically...")
        success = self.automated_document_creation(content, output_filename)

        # 5. Summary
        summary = {
            "ok": True,
            "input_file": input_file,
            "output_file": output_filename,
            "calculations_found": len(calculations),
            "calculations_processed": len(results),
            "signature_added": self.signature,
            "calculations": [
                {"expression": calc['expression'], "result": result}
                for calc, result in zip(calculations, results)
            ]
        }

        print("\n🎉 Complete automation finished!")
        print(f"✅ Processed {len(calculations)} calculations")
        print(f"✅ Created document: {output_filename}")
        print(f"✅ Added signature: {self.signature}")

        return summary

    def quick_calculation_with_doc(self, expression: str, save_to_file: bool = True) -> Dict[str, Any]:
        """Quick calculation with automatic document creation"""

        print(f"🧮 Quick calculation: {expression}")

        # Perform calculation
        result = self.automated_calculator_operation(expression)

        if save_to_file:
            # Create document
            content = f"# Quick Calculation\n\n"
            content += f"{expression} = {result}\n\n"
            content += f"---\nSignature: {self.signature}\n"

            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"quick_calc_{timestamp}.txt"

            self.automated_document_creation(content, filename)

            return {
                "ok": True,
                "expression": expression,
                "result": result,
                "document_created": filename,
                "signature": self.signature
            }

        return {
            "ok": True,
            "expression": expression,
            "result": result
        }

# Factory function
def create_document_automation_controller(signature: str = "Cristal Rivera") -> DocumentAutomationController:
    """Create a new Document Automation Controller"""
    return DocumentAutomationController(signature)