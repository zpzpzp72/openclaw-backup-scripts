import json, collections
from pathlib import Path
import networkx as nx
from graphify.build import build_from_json
from graphify.report import generate

g = json.load(open('graphify-out/graph.json'))
analysis = json.load(open('.graphify_analysis.json'))

# rebuild nx graph with same edges/attrs
G = nx.Graph()
for n in g['nodes']:
    G.add_node(n['id'], **{k: v for k, v in n.items() if k != 'id'})
for l in g['links']:
    s = l.get('source') or l.get('_src')
    t = l.get('target') or l.get('_tgt')
    if s is None or t is None:
        continue
    G.add_edge(s, t, **{k: v for k, v in l.items() if k not in ('source', 'target', '_src', '_tgt')})

communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}

LABELS = {
    0: 'Scout Corpus 2026-10-24 & General Agent Engineering',
    1: 'MCP Registries, SDKs & Multi-Window Scout Snapshots',
    2: 'Agent Memory, Tool Use & Claude Code Ecosystem',
    3: 'Nightly Scout Snapshot 2026-10-30 (Release & Advisory Stream)',
    4: 'MCP Servers, Inspector & Spec Toolchain Security',
    5: 'LLM Inference, Benchmarks & Personalization Systems',
    6: 'Domain Benchmarks, Continual Learning & Data Curation',
    7: 'Multi-Agent Alignment, Theory of Mind & Delegation',
    8: 'OpenAI, Vercel & Agent Skill Planning',
    9: 'Agentic Test Management & Runtime Topology Safety',
    10: 'RL Training, Credit Assignment & Post-Training',
    11: 'Multi-Turn Adversarial Dialogue & Robust Critics',
    12: 'Constrained Decoding & Formal Control',
    13: 'Multi-Agent Optimizer Discovery & Typed DSLs',
    14: 'Recurrent-State Quantization & Gated DeltaNet',
    15: 'Retriever Systems & Search Benchmarks',
    16: 'Numerical Planning & HPlan Benchmarks',
    17: 'Agentic Evaluation Infrastructure & Harbor',
    18: 'Multi-Harness RL Credit Assignment',
    19: 'IRWOZ Dialogue Dataset',
    20: 'Capability Paradox & Indirect Prompt Injection',
    21: 'Scout Research Archive (2026-08-04)',
    22: 'Anthropic Model Hub & Memory Systems',
    23: 'Multi-Harness RL Credit Assignment (Focused)',
    24: 'Agentic TPU Kernel Generation',
    25: 'Richer Models, Riskier Systems',
    26: 'Harbor Adapters & Index Infrastructure',
    27: 'Extremely Sparse Supervision & Reasoning',
    28: 'HarvestBench: Agent Payment & Animal Harm',
    29: 'Indirect Prompt Injection as Test-Time Problem',
    30: 'Removal-Based LLM Faithfulness Improvement',
    31: 'Recurrent-State Write-Back & Memory Limits',
    32: 'MaxKernel TPU Kernel Generation (Focused)',
    33: 'HarvestBench (Focused)',
    34: 'LLM Faithfulness Test-Time (Focused)',
    35: 'Recurrent-State Write-Back (Focused)',
}

from graphify.analyze import suggest_questions

questions = suggest_questions(G, communities, LABELS)
detection = {'total_files': 0, 'total_words': 0, 'warning': 'cluster-only mode — file stats not available'}
report = generate(G, communities, cohesion, LABELS, analysis['gods'], analysis['surprises'],
                  detection, {'input': 0, 'output': 0}, '.', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
Path('.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in LABELS.items()}))
print('report regenerated with', len(LABELS), 'labels;', G.number_of_nodes(), 'nodes', G.number_of_edges(), 'edges')
