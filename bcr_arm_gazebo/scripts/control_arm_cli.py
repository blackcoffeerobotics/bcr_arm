#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time
import math

class ArmControllerCLI(Node):
    """
    A CLI tool to send joint trajectory goals to the BCR ARM.
    """

    def __init__(self):
        super().__init__('arm_controller_cli')
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.joint_names = [
            'joint1',
            'joint2',
            'joint3',
            'joint4',
            'joint5',
            'joint6',
            'joint7'
        ]

        self.predefined_poses = {
            "home": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "ready": [0.0, -0.785, 0.0, -1.57, 0.0, 0.785, 0.0], # Example "ready" pose
            "stretch_up": [0.0, 0.0, 0.0, -math.pi/2, 0.0, 0.0, 0.0], # Pointing upwards
            "forward_low": [0.0, 0.5, 0.7, -1.0, 0.0, 0.5, 0.0] # Example forward and slightly down
        }
        self.get_logger().info("Arm Controller CLI started. Waiting for action server...")
        action_server_name = '/joint_trajectory_controller/follow_joint_trajectory'
        if not self.action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                f"Action server '{action_server_name}' not available after 10 seconds. "
                "Please ensure the joint_trajectory_controller is running."
            )
            raise RuntimeError(f"Action server '{action_server_name}' not available. Initialization failed.")
        self.get_logger().info("Action server found.")


    def send_goal(self, joint_positions, duration_sec=5.0):
        """
        Sends a joint trajectory goal to the action server.

        Args:
            joint_positions (list[float]): A list of target joint positions.
            duration_sec (float): The time in seconds to reach the target.
        """
        if len(joint_positions) != len(self.joint_names):
            self.get_logger().error(
                f"Incorrect number of joint positions. Expected {len(self.joint_names)}, got {len(joint_positions)}"
            )
            return False

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [float(pos) for pos in joint_positions]
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=int((duration_sec % 1) * 1e9))
        # Velocities and accelerations can be left empty for simple position control
        # point.velocities = [0.0] * len(self.joint_names)
        # point.accelerations = [0.0] * len(self.joint_names)

        goal_msg.trajectory.points.append(point)

        self.get_logger().info(f"Sending goal: {joint_positions} to be reached in {duration_sec}s")
        
        future = self.action_client.send_goal_async(goal_msg)
        
        # Optional: Add feedback and result handling if needed
        # rclpy.spin_until_future_complete(self, future)
        # goal_handle = future.result()

        # if not goal_handle.accepted:
        #     self.get_logger().info('Goal rejected :(')
        #     return False

        # self.get_logger().info('Goal accepted :)')
        # result_future = goal_handle.get_result_async()
        # rclpy.spin_until_future_complete(self, result_future)
        # result = result_future.result().result
        # if result.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
        #     self.get_logger().info('Trajectory execution successful!')
        # else:
        #     self.get_logger().info(f'Trajectory execution failed with error code: {result.error_code}')
        # return True
        
        self.get_logger().info("Goal sent. The robot should be moving.")
        return True


    def run_cli(self):
        """
        Runs the command-line interface loop.
        """
        while rclpy.ok():
            print("BCR ARM Control CLI")
            print("--------------------")
            print("Available predefined poses:")
            for i, name in enumerate(self.predefined_poses.keys()):
                print(f"  {i+1}. {name}")
            print("  c. Custom joint angles")
            print("  q. Quit")

            choice = input("Enter your choice: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'c':
                custom_angles_str = input(f"Enter {len(self.joint_names)} joint angles (space-separated, in radians): ").strip()
                try:
                    custom_angles = [float(x) for x in custom_angles_str.split()]
                    if len(custom_angles) == len(self.joint_names):
                        duration = float(input("Enter duration to reach target (seconds, e.g., 5.0): ").strip())
                        self.send_goal(custom_angles, duration_sec=duration)
                    else:
                        self.get_logger().warning(f"Please enter exactly {len(self.joint_names)} angles.")
                except ValueError:
                    self.get_logger().warning("Invalid input. Please enter numbers only.")
            else:
                try:
                    pose_idx = int(choice) - 1
                    pose_names = list(self.predefined_poses.keys())
                    if 0 <= pose_idx < len(pose_names):
                        selected_pose_name = pose_names[pose_idx]
                        target_positions = self.predefined_poses[selected_pose_name]
                        duration = float(input(f"Enter duration to reach '{selected_pose_name}' (seconds, e.g., 5.0): ").strip())
                        self.send_goal(target_positions, duration_sec=duration)
                    else:
                        self.get_logger().warning("Invalid pose number.")
                except ValueError:
                    self.get_logger().warning("Invalid choice. Please enter a number or 'c' or 'q'.")
            
            time.sleep(0.1) # Small delay to allow ROS 2 to process


def main(args=None):
    rclpy.init(args=args)
    arm_controller_cli_node = ArmControllerCLI()
    
    try:
        arm_controller_cli_node.run_cli()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        arm_controller_cli_node.get_logger().error(f"CLI loop error: {e}")
    finally:
        arm_controller_cli_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
