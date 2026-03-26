import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext';

/* ─── Google Font injection ───────────────────────────────────── */
const FontInjector = () => {
    useEffect(() => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap';
        document.head.appendChild(link);
        return () => document.head.removeChild(link);
    }, []);
    return null;
};

/* ─── Team Avatar with img + fallback initials ────────────────── */
const TeamAvatar = ({ img, fallback, ring }) => {
    const [errored, setErrored] = useState(false);

    if (!errored && img) {
        return (
            <img
                src={img}
                alt={fallback}
                onError={() => setErrored(true)}
                className={`w-16 h-16 rounded-full object-cover object-top ring-2 ${ring} bg-gray-100`}
            />
        );
    }

    // Fallback: initials block
    return (
        <div className={`w-16 h-16 rounded-full ring-2 ${ring} bg-blue-100 text-blue-700 flex items-center justify-center text-xl font-bold select-none`}
            style={{ fontFamily: "'DM Serif Display', serif" }}>
            {fallback}
        </div>
    );
};

/* ─── Team Data ───────────────────────────────────────────────── */
const TEAM = [
    {
        name: 'Omer Elfaki',
        role: 'Full-Stack Developer',
        desc: 'Computer science student Full-Stack Developer at CodeLink',
        linkedin: 'https://www.linkedin.com/in/omer-adel-elfaki-5a3050388/',
        img: '/team/OmerElfaki.jpg',
        fallback: 'OE',
        ring: 'ring-violet-200',
        dot: 'bg-violet-500',
    },
    {
        name: 'Osama Almalki',
        role: 'Full-Stack Developer',
        desc: 'Senior CS Student | Software Developer | AI/ML | Data Engineer',
        linkedin: 'https://www.linkedin.com/in/osama-almalki-35685022b/',
        img: '/team/OsamaAlmalki.jpg',
        fallback: 'OA',
        ring: 'ring-sky-200',
        dot: 'bg-sky-500',
    },
    {
        name: 'Omar Mansour',
        role: 'AI Engineer',
        desc: 'Computer science student AI engineer at Node technology',
        linkedin: 'https://www.linkedin.com/in/omar-mansour-5491b7361/',
        img: '/team/OmarMansour.jpg',
        fallback: 'OM',
        ring: 'ring-indigo-200',
        dot: 'bg-indigo-500',
    },
    {
        name: 'Abdulmalik Alabdulwahab',
        role: 'AI & Full-Stack',
        desc: 'AI & Deep Learning Learner | Computer Vision | Full-Stack Developer',
        linkedin: 'https://www.linkedin.com/in/abdulmalik-alabdulwahab',
        img: '/team/AbdulmalikAlabdulwahab.jpg',
        fallback: 'AA',
        ring: 'ring-blue-200',
        dot: 'bg-blue-600',
    },

    {
        name: 'Assoc Prof. Imran Qureshi',
        role: 'Project Supervisor',
        desc: 'Associate Professor at IMSIU, Riyadh + AI Researcher',
        linkedin: 'https://www.linkedin.com/in/imran-qureshi-001213109/',
        img: '/team/ImranQureshi.jpg',
        fallback: 'IQ',
        ring: 'ring-blue-300',
        dot: 'bg-blue-700',
    },
];

const FEATURES = [
    {
        emoji: '🧠',
        bg: 'bg-blue-50',
        icon: 'text-blue-600',
        title: 'ResNet34 U-Net',
        desc: 'State-of-the-art segmentation architecture trained on lung CT datasets for precise pixel-level tumor detection.',
    },
    {
        emoji: '📏',
        bg: 'bg-sky-50',
        icon: 'text-sky-600',
        title: 'RECIST Measurement',
        desc: 'Clinical-grade tumor diameter measurement using convex-hull based RECIST longest axis calculation.',
    },
    {
        emoji: '⚡',
        bg: 'bg-indigo-50',
        icon: 'text-indigo-600',
        title: 'Batch CT Analysis',
        desc: 'Process entire ZIP archives of CT slices simultaneously, ranked by tumor severity for clinical review.',
    },
    {
        emoji: '🔒',
        bg: 'bg-blue-50',
        icon: 'text-blue-600',
        title: 'Secure & Private',
        desc: 'JWT authentication, AWS S3 encrypted storage, and role-based access control for clinical data.',
    },
];

const STAGES = [
    { label: 'Negative', sub: '< 10mm', badge: 'bg-green-100 text-green-800' },
    { label: 'Stage I', sub: '10–39mm', badge: 'bg-yellow-100 text-yellow-800' },
    { label: 'Stage II', sub: '40–69mm', badge: 'bg-orange-100 text-orange-800' },
    { label: 'Stage III', sub: '≥ 70mm', badge: 'bg-red-100 text-red-800' },
];

/* ─── Animated counter ────────────────────────────────────────── */
function useCounter(target, duration = 1800, active = false) {
    const [val, setVal] = useState(0);
    useEffect(() => {
        if (!active) return;
        let start = null;
        const tick = (ts) => {
            if (!start) start = ts;
            const p = Math.min((ts - start) / duration, 1);
            setVal(Math.floor(p * target));
            if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }, [active, target, duration]);
    return val;
}

/* ─── Main ────────────────────────────────────────────────────── */
export default function Homepage() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [scrolled, setScrolled] = useState(false);
    const [statsOn, setStatsOn] = useState(false);
    const statsRef = useRef(null);

    const c1 = useCounter(90, 1600, statsOn);
    const c2 = useCounter(10, 1200, statsOn);
    const c3 = useCounter(4, 900, statsOn);
    const c4 = useCounter(500, 2000, statsOn);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    useEffect(() => {
        const obs = new IntersectionObserver(
            ([e]) => { if (e.isIntersecting) setStatsOn(true); },
            { threshold: 0.3 }
        );
        if (statsRef.current) obs.observe(statsRef.current);
        return () => obs.disconnect();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'DM Sans', sans-serif" }}>
            <FontInjector />

            {/* ── Keyframes ──────────────────────────────────────────── */}
            <style>{`
        @keyframes floatY {
          0%,100% { transform: translateY(0); }
          50%      { transform: translateY(-10px); }
        }
        @keyframes scanBeam {
          0%   { top: 4%; }
          100% { top: 94%; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseRing {
          0%,100% { opacity: .6; transform: scale(1); }
          50%      { opacity: .2; transform: scale(1.06); }
        }
        .anim-float   { animation: floatY   6s ease-in-out infinite; }
        .anim-fadeup  { animation: fadeUp   0.7s ease both; }
        .anim-fadeup2 { animation: fadeUp   0.7s ease 0.15s both; }
        .anim-fadeup3 { animation: fadeUp   0.7s ease 0.3s  both; }
        .anim-pulse   { animation: pulseRing 3s ease-in-out infinite; }
        .scan-beam    { animation: scanBeam 2.5s ease-in-out infinite alternate; }
        .hover-lift   { transition: transform .22s, box-shadow .22s; }
        .hover-lift:hover { transform: translateY(-6px); box-shadow: 0 20px 48px rgba(0,85,255,.10); }
      `}</style>

            {/* ══ NAVBAR ═══════════════════════════════════════════════ */}
            <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-white shadow-md' : 'bg-white/80 backdrop-blur-lg'
                } border-b border-blue-50`}>
                <div className="max-w-6xl mx-auto px-6 flex items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center gap-2 flex-1">
                        <img src="/NewLogo.png" alt="NASMAH" className="h-9 w-auto" />
                        <span className="text-xl font-bold text-gray-900" style={{ fontFamily: "'DM Serif Display', serif" }}>
                            NASMAH
                        </span>
                    </div>

                    {/* Links */}
                    <div className="hidden md:flex items-center gap-8 mr-8">
                        {[['#features', 'Features'], ['#how-it-works', 'How It Works'], ['#team', 'Team']].map(([href, label]) => (
                            <a key={href} href={href}
                                className="text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors">
                                {label}
                            </a>
                        ))}
                    </div>

                    {/* CTA */}
                    <div className="flex items-center gap-3">
                        {isAuthenticated() ? (
                            <Link to="/dashboard">
                                <Button variant="primary" className="text-sm px-4 py-1.5">Dashboard</Button>
                            </Link>
                        ) : (
                            <>
                                <Link to="/login">
                                    <Button variant="outline" className="text-sm px-4 py-1.5">Sign In</Button>
                                </Link>
                                <Link to="/register">
                                    <Button variant="primary" className="text-sm px-4 py-1.5">Get Started</Button>
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </nav>

            {/* ══ HERO ═════════════════════════════════════════════════ */}
            <section className="relative min-h-screen flex items-center pt-16 overflow-hidden"
                style={{ background: 'linear-gradient(155deg, #f0f4ff 0%, #e8f0ff 50%, #f7f8fc 100%)' }}>

                {/* Grid pattern */}
                <div className="absolute inset-0 opacity-40 pointer-events-none"
                    style={{ backgroundImage: 'radial-gradient(rgba(0,85,255,.08) 1px, transparent 1px)', backgroundSize: '28px 28px' }} />
                {/* Glow blob */}
                <div className="absolute top-0 right-0 w-96 h-96 rounded-full pointer-events-none opacity-30"
                    style={{ background: 'radial-gradient(circle, rgba(0,85,255,.15), transparent 70%)', transform: 'translate(30%, -20%)' }} />

                <div className="max-w-6xl mx-auto px-6 py-20 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center w-full">

                    {/* Left copy */}
                    <div>
                        <span className="anim-fadeup inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
                            🫁 AI-Powered Lung Cancer Detection
                        </span>

                        <h1 className="anim-fadeup2 text-5xl lg:text-6xl font-normal leading-tight mb-6 text-gray-900"
                            style={{ fontFamily: "'DM Serif Display', serif", letterSpacing: '-0.02em' }}>
                            Detecting Cancer.<br />
                            <span className="text-blue-600 italic">Earlier.</span> With AI.
                        </h1>

                        <p className="anim-fadeup3 text-lg text-gray-500 leading-relaxed mb-8 max-w-md">
                            NASMAH uses deep learning to analyze lung CT scans, segment tumors with millimeter
                            precision, and classify cancer stages empowering clinicians with actionable AI insights.
                        </p>

                        <div className="anim-fadeup3 flex flex-wrap gap-3 mb-10">
                            {isAuthenticated() ? (
                                <Link to="/dashboard">
                                    <Button variant="primary" className="px-7 py-3 text-base">
                                        Go to Dashboard →
                                    </Button>
                                </Link>
                            ) : (
                                <Link to="/register">
                                    <Button variant="primary" className="px-7 py-3 text-base">
                                        Get Started Free →
                                    </Button>
                                </Link>
                            )}
                            <a href="#how-it-works">
                                <Button variant="outline" className="px-7 py-3 text-base">
                                    See How It Works
                                </Button>
                            </a>
                        </div>

                        {/* Trust pills */}
                        <div className="flex flex-wrap gap-4">
                            {[['📂', 'DICOM & NPY'], ['⚡', 'Batch Processing'], ['📏', 'RECIST Compliant']].map(([ic, lb]) => (
                                <span key={lb} className="flex items-center gap-1.5 text-xs font-medium text-gray-500 bg-white border border-gray-200 rounded-full px-3 py-1.5 shadow-sm">
                                    {ic} {lb}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Right — CT scan visual */}
                    <div className="anim-float relative flex justify-center items-center">
                        {/* Pulse rings */}
                        <div className="anim-pulse absolute w-80 h-80 rounded-full border-2 border-blue-200" />
                        <div className="anim-pulse absolute w-96 h-96 rounded-full border border-blue-100" style={{ animationDelay: '1.2s' }} />

                        {/* Main dark card */}
                        <div className="relative bg-gray-900 rounded-2xl p-5 w-72 shadow-2xl">
                            {/* CT scan mock */}
                            <div className="relative rounded-xl overflow-hidden bg-gray-950 h-52 mb-4">
                                <svg viewBox="0 0 200 180" className="absolute inset-0 w-full h-full opacity-60">
                                    {/* Lung outlines */}
                                    {/* <ellipse cx="70" cy="90" rx="45" ry="62" fill="rgba(255, 100, 100, 0.1)" stroke="rgba(100,150,255,.3)" strokeWidth="1" />
                                    <ellipse cx="130" cy="90" rx="45" ry="62" fill="rgba(100,140,255,.1)" stroke="rgba(100,150,255,.3)" strokeWidth="1" /> */}
                                    <svg width="200" height="180">
                                        <g transform="scale(3) translate(-107 -65)">
                                            <path
                                                d="M135 88 
                                                    C140 78, 150 85, 148 95
                                                    C152 102, 142 110, 132 100
                                                    C128 95, 130 90, 135 88 Z"
                                                fill="rgba(200, 0, 0, 0.53)"
                                            />
                                        </g>
                                    </svg>
                                    {/* Ring overlays */}
                                    {[0, 1, 2, 3].map(i => (
                                        <ellipse key={i} cx="100" cy="90" rx={80 - i * 16} ry={70 - i * 12}
                                            fill="none" stroke={`rgba(100,150,255,${0.04 + i * .01})`} strokeWidth="1" />
                                    ))}
                                    {/* Tumor */}
                                    <circle cx="106" cy="118" r="14" fill="rgba(0, 85, 255, 0.64)" />
                                    <circle cx="106" cy="118" r="9" fill="rgba(0,163,255,.7)" />
                                    <circle cx="106" cy="118" r="4" fill="white" opacity=".9" />
                                    {/* Measurement line */}
                                    <line x1="106" y1="118" x2="102" y2="55" stroke="rgba(0, 200, 255, 0.8)" strokeWidth="2" strokeDasharray="3 3" />
                                    <circle cx="102" cy="55" r="3" fill="rgba(0,200,255,.9)" />
                                </svg>
                                {/* Scanning beam */}
                                <div className="scan-beam absolute left-0 right-0 h-0.5"
                                    style={{ background: 'linear-gradient(90deg, transparent, rgba(0,163,255,.7), transparent)', filter: 'blur(1px)' }} />
                            </div>

                            {/* Result chips */}
                            <div className="flex gap-2 mb-3 flex-wrap">
                                <span className="bg-red-500/20 text-red-300 text-xs font-semibold px-3 py-1 rounded-lg">Stage II Detected</span>
                                <span className="bg-blue-500/20 text-blue-300 text-xs font-semibold px-3 py-1 rounded-lg">42.3 mm</span>
                            </div>

                            {/* Confidence bar */}
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400 text-xs">Confidence</span>
                                <div className="flex items-center gap-2">
                                    <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-blue-600 to-sky-400 rounded-full" style={{ width: '93.2%' }} />
                                    </div>
                                    <span className="text-blue-400 text-xs font-bold">93.2%</span>
                                </div>
                            </div>
                        </div>

                        {/* Floating badges */}
                        <div className="absolute -top-3 -left-6 bg-white rounded-xl shadow-lg border border-gray-100 px-3 py-2"
                            style={{ animation: 'floatY 5s ease-in-out infinite', animationDelay: '1s' }}>
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500" />
                                <span className="text-xs font-semibold text-gray-800">Model Active</span>
                            </div>
                        </div>
                        <div className="absolute -bottom-2 -right-6 bg-white rounded-xl shadow-lg border border-gray-100 px-3 py-2"
                            style={{ animation: 'floatY 7s ease-in-out infinite', animationDelay: '2.2s' }}>
                            <p className="text-xs text-gray-400 mb-0.5">Slices Analyzed</p>
                            <p className="text-xl font-bold text-blue-600" style={{ fontFamily: "'DM Serif Display', serif" }}>247</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ══ STATS BAR ════════════════════════════════════════════ */}
            <section ref={statsRef} className="bg-white border-y border-gray-100 py-12">
                <div className="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                    {[
                        { val: c1, suf: '%', label: 'Model Accuracy', sub: 'on validation set' },
                        { val: c2, suf: '+', label: 'Top Slices', sub: 'per batch analyzed' },
                        { val: c3, suf: '', label: 'Cancer Stages', sub: 'classified by AI' },
                        { val: c4, suf: 'MB', label: 'Max Upload', sub: 'batch ZIP support' },
                    ].map((s, i) => (
                        <div key={i}>
                            <p className="text-5xl font-normal text-blue-600 mb-1" style={{ fontFamily: "'DM Serif Display', serif" }}>
                                {s.val}{s.suf}
                            </p>
                            <p className="text-sm font-700 font-bold text-gray-800">{s.label}</p>
                            <p className="text-xs text-gray-400 mt-0.5">{s.sub}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ══ FEATURES ═════════════════════════════════════════════ */}
            <section id="features" className="py-24 bg-gray-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-14">
                        <span className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-4">
                            ✦ Core Capabilities
                        </span>
                        <h2 className="text-4xl font-normal text-gray-900 mb-3" style={{ fontFamily: "'DM Serif Display', serif" }}>
                            Clinical-grade AI for<br />
                            <em className="text-blue-600 not-italic" style={{ textDecoration: 'underline', textDecorationStyle: 'wavy', textDecorationColor: 'rgba(0,85,255,.35)', textUnderlineOffset: '6px' }}>
                                real-world diagnostics
                            </em>
                        </h2>
                        <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
                            Built for radiologists and researchers who need reliable, explainable AI predictions.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                        {FEATURES.map((f, i) => (
                            <div key={i} className={`hover-lift bg-white rounded-2xl border border-blue-50 p-6 shadow-sm`}>
                                <div className={`${f.bg} w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-5`}>
                                    {f.emoji}
                                </div>
                                <h3 className="font-bold text-gray-900 mb-2 text-base">{f.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ══ HOW IT WORKS ═════════════════════════════════════════ */}
            <section id="how-it-works" className="py-24 bg-white">
                <div className="max-w-5xl mx-auto px-6">
                    <div className="text-center mb-14">
                        <span className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-4">
                            ⟶ Workflow
                        </span>
                        <h2 className="text-4xl font-normal text-gray-900" style={{ fontFamily: "'DM Serif Display', serif" }}>
                            From scan to insight in three steps
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
                        {/* Connector */}
                        <div className="hidden md:block absolute top-10 left-[22%] right-[22%] h-px bg-gradient-to-r from-blue-300 to-sky-300 opacity-50" />

                        {[
                            {
                                step: '01', emoji: '📤', title: 'Upload Your Scan',
                                desc: 'Drop a DICOM, NPY, PNG, or ZIP batch file. The system validates and securely stores it in AWS S3.'
                            },
                            {
                                step: '02', emoji: '🧠', title: 'AI Analyzes',
                                desc: 'ResNet34-UNet segments each CT slice, measures tumor diameters using RECIST methodology, and scores confidence.'
                            },
                            {
                                step: '03', emoji: '📋', title: 'Review Results',
                                desc: 'View stage classification, RECIST diameter overlays, confidence heatmaps, and batch reports.'
                            },
                        ].map((s, i) => (
                            <div key={i} className="relative z-10 bg-gray-50 rounded-2xl border border-blue-50 p-7 text-center hover-lift shadow-sm">
                                <div className="w-16 h-16 rounded-full bg-white border-2 border-blue-200 flex items-center justify-center text-2xl mx-auto mb-4 shadow-sm">
                                    {s.emoji}
                                </div>
                                <p className="text-xs font-bold text-blue-500 uppercase tracking-widest mb-2">Step {s.step}</p>
                                <h3 className="font-bold text-gray-900 mb-2">{s.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed">{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ══ STAGE BANNER ═════════════════════════════════════════ */}
            <section className="py-14 bg-gray-900">
                <div className="max-w-4xl mx-auto px-6 text-center">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-6">
                        Cancer Stage Classification
                    </p>
                    <div className="flex justify-center flex-wrap gap-3">
                        {STAGES.map(s => (
                            <div key={s.label} className={`${s.badge} rounded-xl px-6 py-3 min-w-[120px]`}>
                                <p className="font-bold text-sm">{s.label}</p>
                                <p className="text-xs opacity-70 mt-0.5">{s.sub}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ══ TEAM ═════════════════════════════════════════════════ */}
            <section id="team" className="py-24 bg-gray-50">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="text-center mb-14">
                        <span className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-4">
                            👥 Meet the Team
                        </span>
                        <h2 className="text-4xl font-normal text-gray-900 mb-3" style={{ fontFamily: "'DM Serif Display', serif" }}>
                            The people behind NASMAH
                        </h2>
                        <p className="text-gray-500 max-w-md mx-auto leading-relaxed">
                            A dedicated team of developers, researchers, and medical AI specialists building the future of early lung cancer detection.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
                        {TEAM.map((m, i) => (
                            <div key={i} className="hover-lift bg-white rounded-2xl border border-blue-50 shadow-sm p-6 text-center">
                                {/* Avatar */}
                                <div className="relative w-16 h-16 mx-auto mb-4">
                                    <TeamAvatar img={m.img} fallback={m.fallback} ring={m.ring} />
                                    <div className={`absolute bottom-0 right-0 w-4 h-4 rounded-full ${m.dot} border-2 border-white`} />
                                </div>

                                <h3 className="font-bold text-gray-900 text-sm mb-1">{m.name}</h3>
                                <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-3">{m.role}</p>
                                <p className="text-xs text-gray-500 leading-relaxed mb-4">{m.desc}</p>

                                {m.linkedin !== '#' ? (
                                    <a href={m.linkedin} target="_blank" rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors">
                                        <svg viewBox="0 0 24 24" fill="currentColor" className="w-3 h-3">
                                            <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                                        </svg>
                                        LinkedIn
                                    </a>
                                ) : (
                                    <span className="text-xs text-gray-400 italic">Profile coming soon</span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ══ CTA ══════════════════════════════════════════════════ */}
            <section className="py-24 bg-white text-center">
                <div className="max-w-lg mx-auto px-6">
                    <span className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
                        🚀 Get Started Today
                    </span>
                    <h2 className="text-4xl font-normal text-gray-900 mb-4 leading-tight" style={{ fontFamily: "'DM Serif Display', serif" }}>
                        Ready to revolutionize<br />lung cancer screening?
                    </h2>
                    <p className="text-gray-500 leading-relaxed mb-8">
                        Join NASMAH and bring the power of AI-assisted diagnostics to your clinical workflow. Free to start.
                    </p>
                    <div className="flex justify-center gap-3 flex-wrap">
                        {isAuthenticated() ? (
                            <Link to="/dashboard">
                                <Button variant="primary" className="px-8 py-3 text-base">
                                    Go to Dashboard →
                                </Button>
                            </Link>
                        ) : (
                            <>
                                <Link to="/register">
                                    <Button variant="primary" className="px-8 py-3 text-base">
                                        Create Free Account →
                                    </Button>
                                </Link>
                                <Link to="/login">
                                    <Button variant="secondary" className="px-8 py-3 text-base">
                                        Sign In
                                    </Button>
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </section>

            {/* ══ FOOTER ═══════════════════════════════════════════════ */}
            <footer className="bg-gray-900 text-gray-400 py-10 text-center">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="flex items-center justify-center gap-2 mb-3">
                        <img src="/New_Logo_noBG.png" alt="NASMAH" className="h-12 w-auto opacity-80" />
                        <span className="text-gray-300 font-semibold" style={{ fontFamily: "'DM Serif Display', serif" }}>NASMAH</span>
                        <img src="/CCIS_Logo.png" alt="CCIS Logo" className="h-12 w-auto opacity-80"/>
                        <span className="text-gray-300 font-semibold" style={{ fontFamily: "'DM Serif Display', serif" }}>College of Computer and Information Sciences</span>
                        <img src="/ImamU_logo.png" alt="Imam U Logo" className="h-12 w-auto opacity-80"/>
                        <span className="text-gray-300 font-semibold" style={{ fontFamily: "'DM Serif Display', serif" }}>Al-Imam Mohammad Ibn Saud Islamic University</span>
                    </div>
                    <p className="text-sm mb-1">AI-Powered Lung Cancer Detection System</p>
                    <p className="text-xs opacity-80">
                        Not a substitute for professional medical diagnosis. © 2026 NASMAH Team & CCIS.
                    </p>
                </div>
            </footer>
        </div>
    );
}