from mcp.server.fastmcp import FastMCP
from pathlib import Path
from pydantic import Field
from uuid import uuid4
from dataclasses import dataclass

# import argparse

mcp = FastMCP("Sage MCP Server")


@mcp.tool()
def build_sage_app(
    path: str = Field(description="The path to the Sage app."),
) -> str:
    """Build Sage app."""
    path = path.strip()
    if not Path(path).exists():
        raise FileNotFoundError(f"Could not find repo at {path}")
    return "App image built successfully: registry.sagecontinuum.org/bhupendraraut/cloud-motion:1.24.11.21"


@dataclass
class Deployment:
    uuid: str
    status: str
    nodes: list[str]
    args: list[str]


deployments: dict[str, Deployment] = {}


@mcp.tool()
def deploy_sage_app(
    container_image: str = Field(description="The container image to be deployed."),
    nodes: list[str] = Field(description="The list of nodes to deploy the app to."),
    args: list[str] = Field(description="The arguments to be passed to the app."),
) -> str:
    """Deploy a Sage app."""
    if len(nodes) == 0:
        raise ValueError(
            "No nodes were provided. Please describe which nodes the app should be deployed to."
        )

    # # HACK Validate specific test app arguments.
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--input",
    #     type=str,
    #     nargs=1,
    #     required=True,
    #     help="The camera to be used as input.",
    # )
    # args = parser.parse_args(args=args)

    # TODO Provide mechanism to check if any args are request but missing. This
    # suggets that we need to track this metadata in the app.
    inputs = [arg for arg in args if arg.startswith("--input")]
    if len(inputs) == 0:
        raise ValueError(
            "Argument --input is required. This app requires a camera to be provided as input as --input <camera_name>."
        )
    if len(inputs) > 1:
        raise ValueError("Argument --input must be provided exactly once.")

    # Add deployment to database.
    app_uuid = str(uuid4())
    deployments[app_uuid] = Deployment(
        uuid=app_uuid,
        status="deployed",
        nodes=nodes,
        args=args,
    )
    return f"App deployed successfully! Deployment UUID: {app_uuid}"


@mcp.tool()
def remove_sage_deployment(
    deployment_uuid: str = Field(description="The deployment UUID."),
) -> str:
    """Remove a deployed Sage app."""
    try:
        deployment = deployments[deployment_uuid]
    except KeyError:
        raise ValueError(f"No deployment with UUID {deployment_uuid} found.")
    if deployment.status != "deployed":
        raise ValueError(f"App with ID {deployment_uuid} is not deployed.")
    deployment.status = "removed"
    return "App removed successfully."


@mcp.tool()
def list_sage_deployments() -> str:
    """List all Sage app deployments."""
    output = "UUID STATUS NODES ARGS\n"
    for deployment in deployments.values():
        output += f"{deployment.uuid} {deployment.status} {deployment.nodes} {deployment.args}\n"
    return output


@mcp.tool()
def get_sage_deployment(
    deployment_uuid: str = Field(description="The deployment UUID."),
) -> str:
    """Get status of a Sage app."""
    try:
        deployment = deployments[deployment_uuid]
    except KeyError:
        raise ValueError(f"No deployment with UUID {deployment_uuid} found.")
    return f"Status: {deployment.status}\nNodes: {deployment.nodes}\nArgs: {deployment.args}"


cameras = [
    ("W027", "top_camera", "Sky facing camera."),
    ("W027", "bottom_camera", "Ground facing camera."),
    ("V030", "street-view", "Street facing camera."),
    ("V031", "sky-cam", "Sky facing camera."),
]


@mcp.tool()
def get_cameras() -> str:
    """Get all cameras for all nodes."""
    output = "NODE CAMERA DESCRIPTION\n"
    for node, camera, description in cameras:
        output += f"{node} {camera} {description}\n"
    return output


@mcp.tool()
def get_cameras_for_node(
    node: str = Field(description="Node name."),
) -> str:
    """Gets all cameras for specific node."""
    output = ""
    for node2, camera, description in cameras:
        if node == node2:
            output += f"{camera} {description}\n"
    return output
