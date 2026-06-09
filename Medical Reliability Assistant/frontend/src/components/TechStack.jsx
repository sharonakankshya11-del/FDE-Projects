import { LogoHero } from './Logo.jsx'

const SECTIONS = [
  {
    icon:'⚙️', title:'Language & Runtime',
    rows:[
      ['Python 3.11+','all backend services'],
      ['Node 20+',    'React frontend build only'],
    ],
  },
  {
    icon:'🖥️', title:'Backend Framework',
    rows:[
      ['FastAPI',          'all API routes — async, Pydantic-native, auto OpenAPI docs'],
      ['Uvicorn',          'ASGI server'],
      ['Pydantic v2',      'request / response validation + settings management'],
      ['pydantic-settings','.env file loading with full type coercion'],
    ],
  },
  {
    icon:'🤖', title:'AI & LLM',
    rows:[
      ['GPT-4o-mini',           'agent backbone — Analysis, Maintenance, Recommendation, Guardrails, Eval (via key gateway)'],
      ['text-embedding-3-small','embeddings — 1536-dim, OpenAI API'],
      ['LangGraph',             'multi-agent orchestration — StateGraph with SQLite checkpoints'],
      ['LangChain',             'RecursiveCharacterTextSplitter for document chunking'],
      ['LangSmith',             'observability — traces every agent run, LLM call, retrieval, and HITL feedback'],
    ],
  },
  {
    icon:'🔍', title:'Vector Search & Retrieval',
    rows:[
      ['Pinecone',            'cloud vector store — 20,005 vectors · 1536-dim · cosine · us-east-1'],
      ['BM25Okapi',           'keyword search — in-memory, rank_bm25 library, rebuilt from Pinecone at startup'],
      ['RRF (k=60)',          'Reciprocal Rank Fusion — fuses vector + keyword ranked lists'],
      ['Cross-encoder reranker','reranks top-20 RRF results to top-5 for LLM context'],
    ],
  },
  {
    icon:'📊', title:'Data Pipeline',
    rows:[
      ['AI4I 2020 CSV',             '10,000 rows — primary source (utf-8-sig BOM-safe)'],
      ['predictive_maintenance.csv','10,000 rows — secondary dataset with named Failure Type labels'],
      ['narrative_generator.py',    'maps sensor rows (L/M/H type) → hospital incident narratives'],
      ['Chunk size',                '512 tokens, 64 token overlap — RecursiveCharacterTextSplitter → 20,005 chunks'],
    ],
  },
  {
    icon:'📋', title:'Evaluation',
    rows:[
      ['DeepEval 4.x',  'AnswerRelevancy · Faithfulness · ContextualPrecision · Recall · Relevancy · Hallucination'],
      ['GPT-4o-mini judge','LLM-as-judge for all DeepEval metrics — tone, accuracy, conciseness (GPTJudge)'],
      ['Golden dataset','app/data/golden_dataset.py — curated ground-truth QA pairs'],
      ['LangSmith feedback','HITL approve/edit/reject logged as scored feedback on each run (hitl_decision)'],
    ],
  },
  {
    icon:'🔒', title:'Middleware & Security',
    rows:[
      ['PIIMiddleware',   'strips patient / staff identifiers from all requests and responses'],
      ['Input guardrails','query length check, off-topic classification — gpt-4o-mini classifier'],
      ['Output guardrails','hallucination check + harmful content filter — gpt-4o-mini (no Anthropic required)'],
      ['CORS',           'FastAPI CORSMiddleware — localhost:5173 and localhost:3000'],
    ],
  },
  {
    icon:'🖼️', title:'Frontend',
    rows:[
      ['React 18',              'UI framework — hooks, JSX, functional components only'],
      ['Vite 6',                'build tool + dev server with /api proxy → :8000'],
      ['Recharts',              'BarChart (device health) + RadarChart (eval metrics)'],
      ['Lucide React',          'icon library'],
      ['Catamaran + Source Sans 3','forest-green ECRI-inspired theme (Google Fonts)'],
      ['RecommendationRenderer','markdown → styled section cards with icons and progress bars'],
    ],
  },
  {
    icon:'💾', title:'Persistence & Observability',
    rows:[
      ['Pinecone',      'cloud vector index — medical-equipment · 20,005 vectors · PINECONE_API_KEY'],
      ['SQLite',        './checkpoints.db — LangGraph agent state checkpoints for HITL resumption'],
      ['In-memory dict','_sessions + _run_ids — per-process HITL session store'],
      ['LangSmith',     'project: dr-bleep-medical-reliability · traces + HITL feedback · LANGCHAIN_API_KEY'],
      ['Key gateway',   'keygateway.arshnivlabs.com — OpenAI-compatible proxy for all LLM + embedding calls'],
    ],
  },
]

const PIPELINE = [
  { n:1, name:'User Query',            tag:'natural language input' },
  { n:2, name:'Input Guardrail',       tag:'gpt-4o-mini — safety / off-topic check' },
  { n:3, name:'Retrieval Agent',       tag:'Pinecone + BM25 → RRF → cross-encoder rerank' },
  { n:4, name:'Analysis Agent',        tag:'z-score anomaly detection + gpt-4o-mini summary' },
  { n:5, name:'Maintenance Agent',     tag:'historical pattern matching + gpt-4o-mini summary' },
  { n:6, name:'Recommendation Agent',  tag:'gpt-4o-mini → structured markdown report' },
  { n:7, name:'Output Guardrail',      tag:'gpt-4o-mini — hallucination + harmful content check' },
  { n:8, name:'Human-in-the-Loop',     tag:'approve / edit / reject → LangSmith feedback (1.0 / 0.5 / 0.0)' },
  { n:9, name:'Final Response',        tag:'delivered to engineer + traced in LangSmith' },
]


const card = { background:'#fff', border:'1px solid var(--border)', borderRadius:10, overflow:'hidden', boxShadow:'0 1px 6px rgba(0,0,0,0.05)' }

export default function TechStack() {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:28 }}>

      {/* Logo hero */}
      <LogoHero />

      {/* Table sections */}
      {SECTIONS.map(sec => (
        <div key={sec.title}>
          <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:10 }}>
            <span style={{ fontSize:16 }}>{sec.icon}</span>
            <span style={{ fontFamily:'Catamaran, sans-serif', fontSize:17, fontWeight:800, color:'var(--navy)' }}>{sec.title}</span>
          </div>
          <div style={card}>
            {sec.rows.map(([tech, desc], i) => (
              <div key={tech} style={{
                display:'grid', gridTemplateColumns:'230px 1fr',
                borderBottom: i < sec.rows.length-1 ? '1px solid var(--border-light)' : 'none',
                transition:'background 0.12s',
              }}
                onMouseEnter={e => e.currentTarget.style.background='var(--blue-light)'}
                onMouseLeave={e => e.currentTarget.style.background='transparent'}
              >
                <span style={{
                  padding:'11px 18px', borderRight:'1px solid var(--border-light)',
                  fontFamily:"'SFMono-Regular','Consolas',monospace",
                  fontSize:12.5, fontWeight:700, color:'var(--navy)',
                  display:'flex', alignItems:'center',
                }}>{tech}</span>
                <span style={{ padding:'11px 18px', fontSize:13.5, color:'var(--text-muted)', display:'flex', alignItems:'center', gap:8 }}>
                  <span style={{ color:'var(--blue)', fontWeight:700, flexShrink:0 }}>→</span>{desc}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Pipeline */}
      <div>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:10 }}>
          <span style={{ fontSize:16 }}>🔗</span>
          <span style={{ fontFamily:'Catamaran, sans-serif', fontSize:17, fontWeight:800, color:'var(--navy)' }}>Multi-Agent Pipeline</span>
        </div>
        <div style={card}>
          {PIPELINE.map((step, i) => (
            <div key={step.n} style={{
              display:'flex', alignItems:'center', gap:14, padding:'12px 18px',
              borderBottom: i < PIPELINE.length-1 ? '1px solid var(--border-light)' : 'none',
              transition:'background 0.12s',
            }}
              onMouseEnter={e => e.currentTarget.style.background='var(--blue-light)'}
              onMouseLeave={e => e.currentTarget.style.background='transparent'}
            >
              <div style={{
                width:26, height:26, borderRadius:'50%', background:'var(--navy)',
                color:'#fff', fontSize:11, fontWeight:800,
                display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0,
              }}>{step.n}</div>
              <span style={{ fontSize:14, fontWeight:700, color:'var(--text)', minWidth:200 }}>{step.name}</span>
              <span style={{
                fontFamily:"'SFMono-Regular','Consolas',monospace",
                fontSize:12, color:'var(--blue)',
                background:'var(--blue-light)', border:'1px solid var(--blue-mid)',
                borderRadius:5, padding:'2px 10px',
              }}>{step.tag}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Ports */}
      <div>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:10 }}>
          <span style={{ fontSize:16 }}>🌐</span>
          <span style={{ fontFamily:'Catamaran, sans-serif', fontSize:17, fontWeight:800, color:'var(--navy)' }}>Service Ports</span>
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:12 }}>
          {[
            { label:'FastAPI Backend', port:':8000', desc:'Docs at /docs · Health at /api/health · Architecture at /architecture' },
            { label:'Vite Frontend',   port:':5173', desc:'React dev server · /api proxied to :8000' },
            { label:'LangSmith',       port:'cloud',  desc:'smith.langchain.com · project: dr-bleep-medical-reliability' },
          ].map(p => (
            <div key={p.port} style={{
              ...card, padding:'20px 22px',
              borderTop:'3px solid var(--navy)',
              transition:'box-shadow 0.15s',
            }}
              onMouseEnter={e => e.currentTarget.style.boxShadow='0 4px 16px rgba(45,74,58,0.1)'}
              onMouseLeave={e => e.currentTarget.style.boxShadow='0 1px 6px rgba(0,0,0,0.05)'}
            >
              <div style={{ fontSize:10.5, fontWeight:700, color:'var(--text-light)', textTransform:'uppercase', letterSpacing:'0.6px', marginBottom:6 }}>{p.label}</div>
              <div style={{ fontFamily:'Catamaran, sans-serif', fontSize:34, fontWeight:800, color:'var(--navy)', lineHeight:1 }}>{p.port}</div>
              <div style={{ fontSize:12.5, color:'var(--text-muted)', marginTop:8, lineHeight:1.5 }}>{p.desc}</div>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
