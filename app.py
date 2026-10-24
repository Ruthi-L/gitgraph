from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
import networkx as nx
from pyvis.network import Network
import requests
import os
from database import init_db, record_relationship, get_all_data, get_user_id
from dsa import GitHubGraphDSA

app = Flask(__name__)
GITHUB_API_URL = "https://api.github.com"

# Visual map assigning sharp, clear color codes to distinct interaction paths
COLOR_MAP = {
    "FOLLOWS": "#38bdf8",      # Vivid Sky Blue
    "STARRED": "#facc15",      # Star Yellow
    "FORKED": "#f87171"        # Coral Red
}

# Securely load GitHub Personal Access Token from environment variables if present
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_github_followers(username):
    """Fetch public followers for a user from GitHub REST API."""
    url = f"{GITHUB_API_URL}/users/{username}/followers?per_page=15"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return [user['login'] for user in response.json()]
    except Exception as e:
        print(f"Error fetching followers for {username}: {e}")
    return []

def fetch_github_repos(username):
    """Fetch public repositories for a user."""
    url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=5&sort=updated"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return [repo['name'] for repo in response.json()]
    except Exception as e:
        print(f"Error fetching repos for {username}: {e}")
    return []

def fetch_repo_interactions(username, repo_name):
    """Fetch stargazers and forkers for a given repository to build network edges."""
    interactions = []
    
    # 1. Fetch Stargazers
    stars_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/stargazers?per_page=10"
    try:
        res = requests.get(stars_url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            for user in res.json():
                interactions.append((user['login'], "STARRED"))
    except Exception:
        pass

    # 2. Fetch Forkers
    forks_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/forks?per_page=10"
    try:
        res = requests.get(forks_url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            for fork in res.json():
                if 'owner' in fork and 'login' in fork['owner']:
                    interactions.append((fork['owner']['login'], "FORKED"))
    except Exception:
        pass

    return interactions

def generate_pyvis_graph_html(center_user, highlight_path=None):
    """Generates the interactive topology diagram, highlighting path nodes if provided."""
    users, relationships = get_all_data()
    G = nx.DiGraph()
    
    highlight_set = set(p.lower() for p in highlight_path) if highlight_path else set()

    # 1. Structure Node Canvas Attributes
    for user in users:
        uname = user['username']
        is_in_path = uname.lower() in highlight_set
        is_center = (uname.lower() == center_user.lower())
        
        if is_in_path:
            color = '#9362d8'  # Bright accent purple for shortest path nodes
            size = 28
        elif is_center:
            color = '#5587b7'  # Cornflower blue for center user
            size = 24
        else:
            color = '#cbd5e1'  # Dimmed neutral for other nodes
            size = 14
        
        G.add_node(
            user['id'],
            label=uname,
            title=f"User: {uname}",
            size=size,
            color=color
        )

    # 2. Assign Color and Highlight Edges if they belong to the path sequence
    for rel in relationships:
        follower_id = get_user_id(rel['follower_name'])
        followed_id = get_user_id(rel['followed_name'])
        rel_type = rel['relation_type'].upper()
        
        f_name = rel['follower_name'].lower()
        d_name = rel['followed_name'].lower()
        
        is_edge_in_path = False
        if highlight_path and len(highlight_path) >= 2:
            for i in range(len(highlight_path) - 1):
                if (highlight_path[i].lower() == f_name and highlight_path[i+1].lower() == d_name) or \
                   (highlight_path[i].lower() == d_name and highlight_path[i+1].lower() == f_name):
                    is_edge_in_path = True
                    break

        if is_edge_in_path:
            edge_color = '#9362d8'
            edge_width = 4
        else:
            edge_color = COLOR_MAP.get(rel_type, "#e2e8f0")
            edge_width = 1.5

        G.add_edge(
            follower_id,
            followed_id,
            title=f"Action: {rel_type}",
            color=edge_color,
            width=edge_width,
            arrows='to'
        )

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#0f172a",
        directed=True,
        cdn_resources='remote'
    )
    
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 13,
          "color": "#0f172a",
          "face": "ui-sans-serif, system-ui, sans-serif"
        },
        "borderWidth": 2
      },
      "edges": {
        "font": { "size": 0 },
        "smooth": { "type": "dynamic", "roundness": 0.2 }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.3,
          "springLength": 180,
          "springConstant": 0.02
        }
      }
    }
    """)
    
    net.from_nx(G)
    temp_file_path = os.path.join(app.root_path, 'templates', 'temp_pyvis_graph.html')
    net.save_graph(temp_file_path)
    
    with open(temp_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        
    return html_content

@app.route('/', methods=['GET', 'POST'])
def index():
    center_user = request.args.get('user', 'default_user')
    message = request.args.get('message', "Enter a GitHub username to visualize dynamic interactions.")
    path_result = None
    highlight_path = None
    
    users, relationships = get_all_data()
    dsa_engine = GitHubGraphDSA(users, relationships)
    
    total_nodes = len(users)
    total_edges = len(relationships)
    components = dsa_engine.find_connected_components()
    total_clusters = len(components)

    if request.method == 'POST':
        if 'find_path' in request.form:
            start_u = request.form.get('start_user', '').strip()
            target_u = request.form.get('target_user', '').strip()
            path = dsa_engine.bfs_shortest_path(start_u, target_u)
            if path:
                path_result = " ➔ ".join(path)
                highlight_path = path
                message = f"Shortest path found between {start_u} and {target_u} ({len(path)-1} hops)."
            else:
                message = f"No connection path found between {start_u} and {target_u}."
        else:
            github_username = request.form['username'].strip()
            if not github_username:
                return redirect(url_for('index', user='default_user'))
                
            followers = fetch_github_followers(github_username)
            for follower in followers:
                record_relationship(follower, github_username, "FOLLOWS")
                
            repos = fetch_github_repos(github_username)
            for repo in repos:
                actions = fetch_repo_interactions(github_username, repo)
                for interacting_user, action_type in actions:
                    record_relationship(interacting_user, github_username, action_type)

            message = f"Analyzed active network patterns for {github_username}."
            return redirect(url_for('index', user=github_username, message=message))

    try:
        pyvis_html_content = generate_pyvis_graph_html(center_user, highlight_path=highlight_path)
    except Exception as e:
        pyvis_html_content = f"<h1>Error generating graph structure: {e}</h1>"

    return render_template(
        'index.html',
        graph_html=Markup(pyvis_html_content),
        message=message,
        path_result=path_result,
        total_nodes=total_nodes,
        total_edges=total_edges,
        total_clusters=total_clusters
    )

if __name__ == '__main__':
    init_db()
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, host='0.0.0.0', port=5005)