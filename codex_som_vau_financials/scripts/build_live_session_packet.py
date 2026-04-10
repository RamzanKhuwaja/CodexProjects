"""
build_live_session_packet.py - VAU live session packet builder
"""

from live_workflow import PACKET_PATH, PAYLOAD_TEMPLATE_PATH, build_live_session_packet


def main():
    packet = build_live_session_packet()
    print(f"Saved evidence packet: {PACKET_PATH}")
    print(f"Saved payload template: {PAYLOAD_TEMPLATE_PATH}")
    print("Briefing order:")
    for topic in packet["briefing_order"]:
        print(f"  - {topic}")


if __name__ == "__main__":
    main()
