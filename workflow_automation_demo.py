#!/usr/bin/env python3
"""
Complete Workflow Automation Demo
Shows how Super Interpreter can handle end-to-end automation workflows
"""

import sys
import time
sys.path.append('.')

from controllers.document_automation_controller import create_document_automation_controller

def demo_complete_workflow():
    """Demonstrate complete workflow automation"""
    print("🚀 Complete Workflow Automation Demo")
    print("=" * 60)

    # Initialize document automation controller
    doc_automation = create_document_automation_controller("User")

    print("This demo will:")
    print("1. 📄 Process test_calculations.txt file")
    print("2. 🧮 Extract and perform all calculations automatically")
    print("3. 📝 Create a complete results document")
    print("4. ✍️ Add signature automatically")
    print()

    # Process the file completely
    result = doc_automation.process_file_complete_automation(
        "test_calculations.txt",
        "automated_calculation_results.txt"
    )

    if result["ok"]:
        print("\n🎉 Workflow Automation Complete!")
        print(f"✅ Processed {result['calculations_processed']} calculations")
        print(f"✅ Created document: {result['output_file']}")
        print(f"✅ Added signature: {result['signature_added']}")
        print()
        print("📋 Calculation Summary:")
        for calc in result["calculations"]:
            print(f"   • {calc['expression']} = {calc['result']}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def demo_single_calculation():
    """Demonstrate single calculation with document creation"""
    print("\n" + "="*60)
    print("🧮 Single Calculation Demo: 2819 × 3801")
    print("=" * 60)

    doc_automation = create_document_automation_controller("User")

    result = doc_automation.quick_calculation_with_doc("2819 × 3801", save_to_file=True)

    if result["ok"]:
        print(f"✅ Calculation: {result['expression']} = {result['result']}")
        print(f"✅ Document created: {result['document_created']}")
        print(f"✅ Signature added: {result['signature']}")
    else:
        print("❌ Calculation failed")

if __name__ == "__main__":
    # Run both demos
    demo_complete_workflow()
    time.sleep(2)
    demo_single_calculation()

    print("\n🎉 All automation demos completed!")
    print("Your Super Interpreter now has complete automation capabilities!")