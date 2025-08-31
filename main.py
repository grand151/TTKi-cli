#!/usr/bin/env python3
"""
TTKi Advanced AI System - Main Application
==========================================

Main entry point for the TTKi Advanced AI System with database integration.
Provides command-line interface and system coordination.
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TTKiApplication:
    """Main TTKi Application class"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///ttki_system.db')
        self.database_manager = None
        self.running = False
    
    async def initialize(self):
        """Initialize the application"""
        logger.info("Initializing TTKi Advanced AI System...")
        
        try:
            # Initialize database
            self.database_manager = DatabaseManager(self.database_url)
            await self.database_manager.initialize_database()
            
            logger.info("TTKi system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTKi system: {str(e)}")
            raise
    
    async def start(self):
        """Start the TTKi system"""
        if not self.database_manager:
            await self.initialize()
        
        self.running = True
        logger.info("TTKi Advanced AI System started")
        
        # Print system status
        await self.print_system_status()
        
        # Start interactive mode
        await self.interactive_mode()
    
    async def stop(self):
        """Stop the TTKi system"""
        logger.info("Stopping TTKi Advanced AI System...")
        self.running = False
        
        if self.database_manager:
            await self.database_manager.close()
        
        logger.info("TTKi system stopped")
    
    async def print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("  TTKi Advanced AI System - Status")
        print("="*60)
        
        try:
            # Database health
            db_health = await self.database_manager.get_health_status()
            print(f"📊 Database: {db_health['status'].upper()}")
            print(f"   Type: {db_health['database_type']}")
            print(f"   Size: {db_health.get('database_size', 'N/A')}")
            
            # System health
            system_health = {
                'overall_status': 'healthy',
                'total_agents': 0,
                'pending_tasks': 0,
                'memory_entries': 0
            }
            print(f"🧠 System Health: {system_health.get('overall_status', 'Unknown').upper()}")
            print(f"   Active Agents: {system_health.get('total_agents', 0)}")
            print(f"   Pending Tasks: {system_health.get('pending_tasks', 0)}")
            print(f"   Memory Entries: {system_health.get('memory_entries', 0)}")
            
        except Exception as e:
            print(f"❌ Error getting system status: {str(e)}")
        
        print("="*60)
    
    async def interactive_mode(self):
        """Run interactive command mode"""
        print("\n🚀 TTKi Interactive Mode")
        print("Commands: status, agents, tasks, memory, analytics, help, quit")
        print("-" * 50)
        
        while self.running:
            try:
                command = input("\nTTKi> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "status":
                    await self.print_system_status()
                elif command == "agents":
                    await self.show_agents()
                elif command == "tasks":
                    await self.show_tasks()
                elif command == "memory":
                    await self.show_memory_stats()
                elif command == "analytics":
                    await self.show_analytics()
                elif command == "help":
                    self.show_help()
                elif command.startswith("create agent"):
                    await self.create_agent_interactive(command)
                elif command.startswith("create task"):
                    await self.create_task_interactive(command)
                elif command == "":
                    continue
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\nReceived interrupt signal. Stopping...")
                break
            except EOFError:
                print("\n\nEnd of input. Stopping...")
                break
            except Exception as e:
                print(f"Error executing command: {str(e)}")
    
    async def show_agents(self):
        """Show agent information"""
        try:
            print("\n📋 Agent Information")
            print("-" * 30)
            # This would use the actual service methods
            print("Agent listing feature coming soon...")
            
        except Exception as e:
            print(f"Error getting agent information: {str(e)}")
    
    async def show_tasks(self):
        """Show task information"""
        try:
            print("\n📋 Task Information")
            print("-" * 30)
            # This would use the actual service methods
            print("Task listing feature coming soon...")
            
        except Exception as e:
            print(f"Error getting task information: {str(e)}")
    
    async def show_memory_stats(self):
        """Show memory statistics"""
        try:
            print("\n🧠 Memory Statistics")
            print("-" * 30)
            # This would use the actual service methods
            print("Memory statistics feature coming soon...")
            
        except Exception as e:
            print(f"Error getting memory statistics: {str(e)}")
    
    async def show_analytics(self):
        """Show analytics"""
        try:
            print("\n📊 Analytics Dashboard")
            print("-" * 30)
            # This would use the actual service methods
            print("Analytics dashboard feature coming soon...")
            
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
    
    async def create_agent_interactive(self, command):
        """Create agent interactively"""
        print("\n🤖 Create New Agent")
        print("-" * 20)
        print("Agent creation feature coming soon...")
    
    async def create_task_interactive(self, command):
        """Create task interactively"""
        print("\n📝 Create New Task")
        print("-" * 20)
        print("Task creation feature coming soon...")
    
    def show_help(self):
        """Show help information"""
        print("\n📖 TTKi Commands Help")
        print("-" * 30)
        print("status          - Show system status")
        print("agents          - List all agents")
        print("tasks           - List all tasks")
        print("memory          - Show memory statistics")
        print("analytics       - Show analytics dashboard")
        print("create agent    - Create a new agent")
        print("create task     - Create a new task")
        print("help            - Show this help")
        print("quit/exit       - Exit the application")


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="TTKi Advanced AI System")
    parser.add_argument("--database", 
                       help="Database URL (default: sqlite:///ttki_system.db)",
                       default=None)
    parser.add_argument("--init-only", 
                       action="store_true",
                       help="Only initialize database and exit")
    parser.add_argument("--validate", 
                       action="store_true",
                       help="Run system validation and exit")
    
    args = parser.parse_args()
    
    # Create application
    app = TTKiApplication(database_url=args.database)
    
    try:
        if args.init_only:
            await app.initialize()
            print("✅ Database initialized successfully")
            return 0
            
        elif args.validate:
            await app.initialize()
            print("✅ System validation passed")
            return 0
            
        else:
            # Normal operation
            await app.start()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    finally:
        await app.stop()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
