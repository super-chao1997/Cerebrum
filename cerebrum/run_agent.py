#!/usr/bin/env python
from cerebrum.manager.agent import AgentManager
import argparse
import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run agent")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--agent_path", help="Local path to the agent directory")
    group.add_argument("--agent_author", help="Author of the remote agent")
    
    parser.add_argument("--agent_name", help="Name of the remote agent (required if --agent_author is provided)")
    parser.add_argument("--agent_version", help="Specific version of the agent to run (optional)")
    parser.add_argument("--agenthub_url", default="https://app.aios.foundation", 
                        help="Base URL for the Cerebrum API (default: https://app.aios.foundation)")
    parser.add_argument("--task_input", help="Task input for the agent", default="")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Path to a JSON config file for the agent")
    parser.add_argument("--mode", choices=["local", "remote"], 
                        help="Explicitly specify loading mode: 'local' for local files, 'remote' for remote download")
    
    args = parser.parse_args()
    
    if args.agent_author and not args.agent_name:
        parser.error("--agent_name is required when --agent_author is provided")
    
    if args.agent_path and args.mode == "remote":
        parser.error("Cannot use --mode=remote with --agent_path (use --agent_author and --agent_name instead)")
    
    if args.agent_author and args.mode == "local":
        parser.error("Cannot use --mode=local with --agent_author (use --agent_path instead)")
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('cerebrum').setLevel(logging.DEBUG)
    
    manager = AgentManager(args.agenthub_url)
    
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    try:
        # Determine loading mode
        load_mode = args.mode
        if not load_mode:
            load_mode = "local" if args.agent_path else "remote"
        
        logger.info(f"Agent loading mode: {load_mode}")
        
        if load_mode == "local":
            logger.info(f"Running agent from local path: {args.agent_path}")
            
            if not os.path.exists(args.agent_path):
                logger.error(f"Path does not exist: {args.agent_path}")
                sys.exit(1)
            
            agent_class, agent_config = manager.load_agent(local=True, path=args.agent_path)
            logger.info(f"Loaded local agent: {agent_config.get('name', 'unknown')}")
            
        else:  # remote mode
            logger.info(f"Running remote agent: {args.agent_author}/{args.agent_name}")
            
            try:
                cached_versions = manager._get_cached_versions(args.agent_author, args.agent_name)
                version_to_use = args.agent_version or (manager.get_newest_version(cached_versions) if cached_versions else None)
                
                if version_to_use and version_to_use in cached_versions:
                    logger.info(f"Using cached version: {version_to_use}")
                else:
                    logger.info(f"Downloading agent {args.agent_author}/{args.agent_name}" + 
                                (f" (version {args.agent_version})" if args.agent_version else ""))
                    author, name, version = manager.download_agent(args.agent_author, args.agent_name, args.agent_version)
                    version_to_use = version
                    logger.info(f"Downloaded agent version: {version_to_use}")
            except Exception as e:
                logger.error(f"Failed to download agent: {e}")
                sys.exit(1)
            
            agent_class, agent_config = manager.load_agent(
                author=args.agent_author, 
                name=args.agent_name, 
                version=version_to_use
            )
            logger.info(f"Loaded remote agent: {args.agent_author}/{args.agent_name} (v{version_to_use})")
        
        merged_config = {**agent_config, **config}
        
        agent_name = merged_config.get('name', 'unknown')
        logger.info(f"Initializing agent: {agent_name}")
        agent = agent_class(agent_name)
        
        logger.info(f"Running agent: {agent_name}")
        result = agent.run(args.task_input)
        
        logger.info(f"Agent execution completed")
        logger.info(f"Result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
