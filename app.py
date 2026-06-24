from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
import networkx as nx
from pyvis.network import Network
import requests
import os
from database import init_db, record_relationship, get_all_data, get_user_id

# Re-initialize clean schemas
init_db()

app = Flask(__name__)
GITHUB_API_URL = "https://api.github.com"

# Visual map assigning sharp, clear color codes to distinct interaction paths
COLOR_MAP = {
    "FOLLOWS": "#38bdf8",      # Vivid Sky Blue
    "STARRED": "#facc15",      # Star Yellow
    "FORKED": "#f87171"        # Coral Red
}

# Optional: Add your token if you hit rate limits ("Authorization": "token YOUR_PAT")
HEADERS = {}

def fetch_github_followers(username):
    """Fetches social pathways to model standard platform followers mapping."""
    url = f"{GITHUB_API_URL}/users/{username}/followers?per_page=8"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return [f.get('login') for f in response.json() if f.get('login')]
        return []
    except Exception as e:
        print(f"Followers fetch failure: {e}")
        return []

def fetch_github_repos(username):
    """Discovers repository targets owned by the developer profile."""
    url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=3&sort=updated"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return [r.get('name') for r in response.json() if r.get('name')]
        return []
    except Exception as e:
        print(f"Repositories fetch failure: {e}")
        return []

def fetch_repo_interactions(username, repo_name):
    """Extracts technical cross-reference data points (Stars & Forks) from project codebases."""
    interactions = []
    
    # A. Pull stargazers metrics
    stars_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/stargazers?per_page=3"
    try:
        res = requests.get(stars_url, headers=HEADERS)
        if res.status_code == 200:
            for user in res.json():
                if user.get('login'):
                    interactions.append((user.get('login'), "STARRED"))
    except Exception as e:
        print(f"Stargazers processing check skipped: {e}")

    # B. Pull fork development pathways
    forks_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/forks?per_page=3"
    try:
        res = requests.get(forks_url, headers=HEADERS)
        if res.status_code == 200:
            for fork in res.json():
                owner = fork.get('owner', {})
                if owner.get('login'):
                    interactions.append((owner.get('login'), "FORKED"))
    except Exception as e:
        print(f"Forks processing check skipped: {e}")

    return interactions

def generate_pyvis_graph_html(center_user):
    """Generates the interactive topology diagram, completely removing text label outlines."""
    users, relationships = get_all_data()
    G = nx.DiGraph()

    # 1. Structure Node Canvas Attributes
    for user in users:
        is_center = (user['username'].lower() == center_user.lower())
        color = '#a855f7' if is_center else '#4b5563'
        size = 35 if is_center else 16
        
        G.add_node(
            user['id'],
            label=user['username'],
            title=f"User: {user['username']}",
            size=size,
            color=color
        )

    # 2. Assign Color and Labels to Edges Based on Interaction Types
    for rel in relationships:
        follower_id = get_user_id(rel['follower_name'])
        followed_id = get_user_id(rel['followed_name'])
        rel_type = rel['relation_type'].upper()
        
        relation_color = COLOR_MAP.get(rel_type, "#94a3b8")
        G.add_edge(
            follower_id,
            followed_id,
            title=f"Action: {rel_type}",
            color=relation_color,
            label=rel_type,
            width=2,
            arrows='to'
        )

    # 3. Initialize Pyvis Viewport Instance
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#121214", # Matches theme canvas background
        font_color="white",
        directed=True,
        cdn_resources='remote'
    )
    
    # CRITICAL OPTIONS: strokeWidth set to 0 handles clean label visibility without blank white box lines
    net.set_options("""
    {
      "edges": {
        "font": {
          "strokeWidth": 0,
          "color": "#cbd5e1",
          "size": 11,
          "align": "top"
        },
        "smooth": {
          "type": "continuous"
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -3000,
          "centralGravity": 0.2,
          "springLength": 120,
          "springConstant": 0.04
        }
      }
    }
    """)
    
    net.from_nx(G)
    
    # Build safely to dynamic injection template
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
    message = "Enter a GitHub username to visualize dynamic interactions."
    
    if request.method == 'POST':
        github_username = request.form['username'].strip()
        if not github_username:
            return redirect(url_for('index', user='default_user'))
            
        # 1. Map Social Pathways (FOLLOWS)
        followers = fetch_github_followers(github_username)
        for follower in followers:
            record_relationship(follower, github_username, "FOLLOWS")
            
        # 2. Map Repository Actions (STARRED & FORKED)
        repos = fetch_github_repos(github_username)
        action_count = 0
        for repo in repos:
            actions = fetch_repo_interactions(github_username, repo)
            for interacting_user, action_type in actions:
                record_relationship(interacting_user, github_username, action_type)
                action_count += 1

        if (len(followers) + action_count) > 0:
            message = f"Analyzed active network patterns for {github_username}."
        else:
            message = "Profile processed. No connections found or rate limiting bounds active."

        return redirect(url_for('index', user=github_username, message=message))

    if request.args.get('message'):
        message = request.args.get('message')

    try:
        pyvis_html_content = generate_pyvis_graph_html(center_user)
    except Exception as e:
        pyvis_html_content = f"<h1>Error generating graph structure: {e}</h1>"

    return render_template(
        'index.html',
        graph_html=Markup(pyvis_html_content),
        message=message
    )

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, host='0.0.0.0', port=5005)