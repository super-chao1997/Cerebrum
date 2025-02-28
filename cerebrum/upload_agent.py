from cerebrum.manager.agent import AgentManager

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload agents")
    parser.add_argument(
        "--agent_path",
        required=True
    )
    parser.add_argument(
        "--base_url",
        # default="https://app.aios.foundation"
        default="http://localhost:3000"
    )
    args = parser.parse_args()

    manager = AgentManager(args.base_url)

    agent_package = manager.package_agent(args.agent_path)

    manager.upload_agent(agent_package)
