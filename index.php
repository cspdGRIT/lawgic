<?php
// Lawgic Landing Page - PHP Version
// You can add dynamic PHP functionality here if needed

// Example: Dynamic year for copyright
$current_year = date('Y');

// Example: You could add database connections, form processing, etc. here
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lawgic - India's First AI-Powered Legal Assistance Platform</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header */
        header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }

        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-image {
            height: 45px;
            width: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }

        .logo-image:hover {
            transform: scale(1.05);
        }

        .logo-text {
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(45deg, #60a5fa, #a5f3fc);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav-links a {
            color: white;
            text-decoration: none;
            transition: color 0.3s;
        }

        .nav-links a:hover {
            color: #60a5fa;
        }

        .investor-button {
            background: linear-gradient(45deg, #fbbf24, #f59e0b);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(251, 191, 36, 0.3);
        }

        .investor-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(251, 191, 36, 0.4);
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            padding: 120px 0 80px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="50" cy="50" r="0.5" fill="%23ffffff" opacity="0.15"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            animation: float 20s infinite linear;
            pointer-events: none;
        }

        @keyframes float {
            0% { transform: translateX(-50%) translateY(-50%); }
            100% { transform: translateX(-50%) translateY(-60%); }
        }

        .hero-content {
            position: relative;
            z-index: 2;
        }

        .hero-logo {
            margin: 0 auto 2rem;
            display: block;
            height: 120px;
            width: auto;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: logoGlow 3s ease-in-out infinite alternate;
        }

        @keyframes logoGlow {
            from { 
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                transform: scale(1);
            }
            to { 
                box-shadow: 0 15px 40px rgba(96, 165, 250, 0.4);
                transform: scale(1.02);
            }
        }

        .hero h1 {
            font-size: 3.8rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #60a5fa, #a5f3fc, #fbbf24);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { filter: brightness(1); }
            to { filter: brightness(1.2); }
        }

        .hero p {
            font-size: 1.4rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #fbbf24;
            display: block;
        }

        .stat-label {
            font-size: 1rem;
            opacity: 0.8;
        }

        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .cta-button {
            display: inline-block;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(59, 130, 246, 0.4);
        }

        .cta-secondary {
            background: linear-gradient(45deg, #059669, #10b981);
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        }

        .cta-secondary:hover {
            box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
        }

        /* Market Opportunity */
        .market-opportunity {
            padding: 80px 0;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        }

        .section-title {
            text-align: center;
            font-size: 2.8rem;
            margin-bottom: 3rem;
            color: #1e293b;
        }

        .market-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }

        .market-card {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            border: 1px solid #f3f4f6;
            transition: transform 0.3s;
            position: relative;
        }

        .market-card:hover {
            transform: translateY(-10px);
        }

        .market-card::before {
            content: '';
            position: absolute;
            top: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: url('logo.jpg') center/cover;
            border-radius: 8px;
            opacity: 0.1;
        }

        .market-number {
            font-size: 3rem;
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 1rem;
        }

        .market-label {
            font-size: 1.2rem;
            color: #1e293b;
            font-weight: 600;
        }

        .market-desc {
            color: #64748b;
            margin-top: 1rem;
        }

        /* Advanced Features */
        .features {
            padding: 80px 0;
            background: #f8fafc;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 3rem;
        }

        .feature-card {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            border: 1px solid #e2e8f0;
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
        }

        .feature-card::after {
            content: '';
            position: absolute;
            top: 15px;
            right: 15px;
            width: 30px;
            height: 30px;
            background: url('logo.jpg') center/cover;
            border-radius: 6px;
            opacity: 0.05;
        }

        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .feature-icon {
            width: 70px;
            height: 70px;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
        }

        .feature-icon i {
            color: white;
            font-size: 1.8rem;
        }

        .feature-card h3 {
            font-size: 1.6rem;
            margin-bottom: 1rem;
            color: #1e293b;
        }

        .feature-card p {
            color: #64748b;
            line-height: 1.7;
            margin-bottom: 1.5rem;
        }

        .feature-badge {
            background: linear-gradient(45deg, #fbbf24, #f59e0b);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
        }

        /* Business Model */
        .business-model {
            padding: 80px 0;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
        }

        .revenue-streams {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .revenue-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 2.5rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s;
            position: relative;
        }

        .revenue-card::before {
            content: '';
            position: absolute;
            top: 15px;
            right: 15px;
            width: 25px;
            height: 25px;
            background: url('logo.jpg') center/cover;
            border-radius: 4px;
            opacity: 0.2;
        }

        .revenue-card:hover {
            transform: translateY(-5px);
        }

        .revenue-icon {
            font-size: 3rem;
            color: #fbbf24;
            margin-bottom: 1.5rem;
        }

        .revenue-card h3 {
            font-size: 1.4rem;
            margin-bottom: 1rem;
            color: #60a5fa;
        }

        .revenue-amount {
            font-size: 1.8rem;
            font-weight: bold;
            color: #fbbf24;
            margin-bottom: 0.5rem;
        }

        /* Competitive Advantages */
        .competitive-advantages {
            padding: 80px 0;
            background: white;
        }

        .advantages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .advantage-card {
            padding: 2rem;
            border-radius: 15px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid #3b82f6;
            transition: transform 0.3s;
            position: relative;
        }

        .advantage-card::after {
            content: '';
            position: absolute;
            top: 10px;
            right: 10px;
            width: 20px;
            height: 20px;
            background: url('logo.jpg') center/cover;
            border-radius: 4px;
            opacity: 0.1;
        }

        .advantage-card:hover {
            transform: scale(1.05);
        }

        .advantage-icon {
            font-size: 2.5rem;
            color: #3b82f6;
            margin-bottom: 1rem;
        }

        /* Technology Stack */
        .tech-stack {
            padding: 80px 0;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
        }

        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .tech-item {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s;
            position: relative;
        }

        .tech-item::before {
            content: '';
            position: absolute;
            top: 10px;
            right: 10px;
            width: 20px;
            height: 20px;
            background: url('logo.jpg') center/cover;
            border-radius: 4px;
            opacity: 0.2;
        }

        .tech-item:hover {
            transform: scale(1.05);
        }

        .tech-item i {
            font-size: 3rem;
            color: #fbbf24;
            margin-bottom: 1rem;
        }

        /* Demo Section */
        .demo-section {
            padding: 80px 0;
            background: #f8fafc;
            text-align: center;
        }

        .demo-video {
            max-width: 800px;
            margin: 3rem auto;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        }

        .demo-placeholder {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
            padding: 6rem 2rem;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 2rem;
            position: relative;
        }

        .demo-placeholder::before {
            content: '';
            position: absolute;
            top: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: url('logo.jpg') center/cover;
            border-radius: 8px;
            opacity: 0.3;
        }

        .play-button {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #3b82f6, #8b5cf6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.3s;
        }

        .play-button:hover {
            transform: scale(1.1);
        }

        .play-button i {
            font-size: 2rem;
            margin-left: 5px;
        }

        /* Investor CTA */
        .investor-cta {
            padding: 80px 0;
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white;
            text-align: center;
            position: relative;
        }

        .investor-cta::before {
            content: '';
            position: absolute;
            top: 30px;
            left: 30px;
            width: 60px;
            height: 60px;
            background: url('logo.jpg') center/cover;
            border-radius: 12px;
            opacity: 0.2;
        }

        .investor-cta::after {
            content: '';
            position: absolute;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: url('logo.jpg') center/cover;
            border-radius: 12px;
            opacity: 0.2;
        }

        .investor-content {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }

        .investor-highlights {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }

        .highlight-item {
            text-align: center;
        }

        .highlight-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #fbbf24;
        }

        /* Footer */
        footer {
            background: #0f172a;
            color: white;
            padding: 60px 0 20px;
            position: relative;
        }

        .footer-logo {
            height: 60px;
            width: auto;
            margin-bottom: 1rem;
            border-radius: 8px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
            margin-bottom: 2rem;
        }

        .footer-section h3 {
            margin-bottom: 1rem;
            color: #60a5fa;
        }

        .footer-section p,
        .footer-section a {
            color: #94a3b8;
            text-decoration: none;
            line-height: 1.6;
        }

        .footer-section a:hover {
            color: #60a5fa;
        }

        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #334155;
            color: #64748b;
            position: relative;
        }

        .footer-bottom::before {
            content: '';
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 30px;
            background: url('logo.jpg') center/cover;
            border-radius: 6px;
            opacity: 0.3;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero p {
                font-size: 1.1rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .hero-stats {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
            
            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }

            .hero-logo {
                height: 80px;
            }

            .logo-image {
                height: 35px;
            }
        }

        /* Animations */
        .fade-in {
            opacity: 0;
            transform: translateY(30px);
            animation: fadeIn 1s forwards;
        }

        @keyframes fadeIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-delay-1 { animation-delay: 0.2s; }
        .animate-delay-2 { animation-delay: 0.4s; }
        .animate-delay-3 { animation-delay: 0.6s; }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Logo watermark for sections */
        .section-with-logo::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            background: url('logo.jpg') center/cover;
            border-radius: 20px;
            opacity: 0.02;
            pointer-events: none;
            z-index: 0;
        }

        .section-with-logo {
            position: relative;
        }

        .section-with-logo > .container {
            position: relative;
            z-index: 1;
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo-container">
                <img src="logo.jpg" alt="Lawgic Logo" class="logo-image">
                <div class="logo-text">Lawgic</div>
            </div>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#market">Market</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#business">Business Model</a></li>
                <li><a href="#demo">Demo</a></li>
            </ul>
            <a href="#investor" class="investor-button">
                <i class="fas fa-chart-line"></i> Investors
            </a>
        </nav>
    </header>

    <section id="home" class="hero">
        <div class="container">
            <div class="hero-content fade-in">
                <img src="logo.jpg" alt="Lawgic - AI Legal Platform" class="hero-logo">
                <h1>Disrupting India's ₹4.2L Cr Legal Market</h1>
                <p>First AI-powered legal platform combining RAG technology, multilingual support, and predictive analytics. Democratizing justice for 1.4B Indians through intelligent automation and seamless lawyer-client connections.</p>
                
                <div class="hero-stats">
                    <div class="stat-item">
                        <span class="stat-number">₹4.2L Cr</span>
                        <span class="stat-label">Total Addressable Market</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">95%</span>
                        <span class="stat-label">Cases Lack AI Support</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">15M+</span>
                        <span class="stat-label">Pending Court Cases</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">22</span>
                        <span class="stat-label">Official Languages</span>
                    </div>
                </div>

                <div class="cta-buttons">
                    <a href="#demo" class="cta-button">Watch Demo</a>
                    <a href="#investor" class="cta-button cta-secondary">Investment Deck</a>
                </div>
            </div>
        </div>
    </section>

    <section id="market" class="market-opportunity section-with-logo">
        <div class="container">
            <h2 class="section-title">Massive Market Opportunity</h2>
            <div class="market-stats">
                <div class="market-card">
                    <div class="market-number">₹4.2L Cr</div>
                    <div class="market-label">Indian Legal Services Market</div>
                    <div class="market-desc">Growing at 8.2% CAGR with increasing digitization demand</div>
                </div>
                <div class="market-card">
                    <div class="market-number">1.7M</div>
                    <div class="market-label">Registered Lawyers</div>
                    <div class="market-desc">Fragmented market with limited tech adoption</div>
                </div>
                <div class="market-card">
                    <div class="market-number">450M+</div>
                    <div class="market-label">Internet Users</div>
                    <div class="market-desc">Rapidly adopting digital-first legal solutions</div>
                </div>
            </div>
        </div>
    </section>

    <section id="features" class="features">
        <div class="container">
            <h2 class="section-title">Revolutionary AI-Powered Features</h2>
            <div class="features-grid">
                <?php
                // PHP array of features - you can easily modify or add features from database
                $features = [
                    [
                        'icon' => 'fas fa-brain',
                        'title' => 'Predictive Case Analytics',
                        'description' => 'ML algorithms analyze 10M+ case histories to predict outcomes with 87% accuracy, giving clients data-driven insights.',
                        'badge' => 'Patent Pending'
                    ],
                    [
                        'icon' => 'fas fa-language',
                        'title' => '22-Language AI Assistant',
                        'description' => 'Voice-powered legal guidance in all Indian languages with real-time translation and cultural context understanding.',
                        'badge' => 'First in India'
                    ],
                    [
                        'icon' => 'fas fa-magic',
                        'title' => 'Smart Document Generator',
                        'description' => 'AI creates legally compliant documents in minutes with state-specific variations and automatic compliance checks.',
                        'badge' => 'Time Saver'
                    ],
                    [
                        'icon' => 'fas fa-eye',
                        'title' => 'AR Document Scanner',
                        'description' => 'Advanced OCR with AR overlay extracts and verifies legal documents instantly with 99.2% accuracy.',
                        'badge' => 'Innovative'
                    ],
                    [
                        'icon' => 'fas fa-shield-alt',
                        'title' => 'Blockchain Verification',
                        'description' => 'Immutable document authentication integrated with Aadhaar and DigiLocker for tamper-proof legal records.',
                        'badge' => 'Secure'
                    ],
                    [
                        'icon' => 'fas fa-robot',
                        'title' => 'AI Legal Arbitrator',
                        'description' => 'First AI-powered dispute resolution system for small claims, reducing resolution time from months to days.',
                        'badge' => 'Revolutionary'
                    ],
                    [
                        'icon' => 'fas fa-chart-line',
                        'title' => 'Real-time Court Integration',
                        'description' => 'Live case tracking with eCourts API integration, automated deadline reminders, and hearing notifications.',
                        'badge' => 'Connected'
                    ],
                    [
                        'icon' => 'fas fa-network-wired',
                        'title' => 'Lawyer Network Platform',
                        'description' => 'AI-powered matching algorithm connects clients with specialized lawyers based on case type, location, and success rate.',
                        'badge' => 'Smart Matching'
                    ],
                    [
                        'icon' => 'fas fa-graduation-cap',
                        'title' => 'Legal Education Hub',
                        'description' => 'Gamified legal literacy platform with AI tutors, making law accessible to rural and underserved communities.',
                        'badge' => 'Social Impact'
                    ]
                ];

                foreach ($features as $feature): ?>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="<?php echo $feature['icon']; ?>"></i>
                    </div>
                    <h3><?php echo $feature['title']; ?></h3>
                    <p><?php echo $feature['description']; ?></p>
                    <span class="feature-badge"><?php echo $feature['badge']; ?></span>
                </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>

    <section id="business" class="business-model">
        <div class="container">
            <h2 class="section-title">Multiple Revenue Streams</h2>
            <div class="revenue-streams">
                <?php
                // PHP array of revenue streams
                $revenue_streams = [
                    [
                        'icon' => 'fas fa-users',
                        'title' => 'SaaS Subscriptions',
                        'amount' => '₹299-2999/month',
                        'description' => 'Tiered pricing for individuals, lawyers, and law firms'
                    ],
                    [
                        'icon' => 'fas fa-percentage',
                        'title' => 'Transaction Fees',
                        'amount' => '3-8% commission',
                        'description' => 'On lawyer consultations and document services'
                    ],
                    [
                        'icon' => 'fas fa-building',
                        'title' => 'Enterprise Solutions',
                        'amount' => '₹2L-50L/year',
                        'description' => 'Custom AI solutions for law firms and corporations'
                    ],
                    [
                        'icon' => 'fas fa-file-alt',
                        'title' => 'Document Processing',
                        'amount' => '₹50-500/doc',
                        'description' => 'Pay-per-document for AI generation and verification'
                    ],
                    [
                        'icon' => 'fas fa-handshake',
                        'title' => 'AI Arbitration',
                        'amount' => '₹1000-10000/case',
                        'description' => 'Automated dispute resolution for small claims'
                    ],
                    [
                        'icon' => 'fas fa-chart-bar',
                        'title' => 'Analytics & Insights',
                        'amount' => '₹5000-50000/report',
                        'description' => 'Legal market intelligence and case analytics'
                    ]
                ];

                foreach ($revenue_streams as $stream): ?>
                <div class="revenue-card">
                    <div class="revenue-icon">
                        <i class="<?php echo $stream['icon']; ?>"></i>
                    </div>
                    <h3><?php echo $stream['title']; ?></h3>
                    <div class="revenue-amount"><?php echo $stream['amount']; ?></div>
                    <p><?php echo $stream['description']; ?></p>
                </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>

    <section class="competitive-advantages section-with-logo">
        <div class="container">
            <h2 class="section-title">Unfair Competitive Advantages</h2>
            <div class="advantages-grid">
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-first-aid"></i>
                    </div>
                    <h3>First Mover Advantage</h3>
                    <p>First AI-powered legal platform in India with multilingual support and predictive analytics</p>
                </div>
                
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-database"></i>
                    </div>
                    <h3>Proprietary Dataset</h3>
                    <p>10M+ curated legal documents and case histories in multiple Indian languages</p>
                </div>
                
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-network-wired"></i>
                    </div>
                    <h3>Network Effects</h3>
                    <p>Platform becomes more valuable as more lawyers and clients join the ecosystem</p>
                </div>
                
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-cog"></i>
                    </div>
                    <h3>API Integrations</h3>
                    <p>Direct partnerships with eCourts, DigiLocker, and government legal databases</p>
                </div>
                
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-graduation-cap"></i>
                    </div>
                    <h3>Technical Expertise</h3>
                    <p>Team combines legal knowledge with cutting-edge AI/ML capabilities</p>
                </div>
                
                <div class="advantage-card">
                    <div class="advantage-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>Regulatory Compliance</h3>
                    <p>Built-in compliance with Indian legal standards and data protection laws</p>
                </div>
            </div>
        </div>
    </section>

    <section id="technology" class="tech-stack">
        <div class="container">
            <h2 class="section-title">Enterprise-Grade Technology</h2>
            <div class="tech-grid">
                <div class="tech-item">
                    <i class="fas fa-brain"></i>
                    <h3>Custom RAG System</h3>
                    <p>Proprietary legal knowledge base</p>
                </div>
                <div class="tech-item">
                    <i class="fab fa-python"></i>
                    <h3>Python + FastAPI</h3>
                    <p>High-performance backend</p>
                </div>
                <div class="tech-item">
                    <i class="fas fa-database"></i>
                    <h3>PostgreSQL + Vector DB</h3>
                    <p>Scalable data architecture</p>
                </div>
                <div class="tech-item">
                    <i class="fab fa-react"></i>
                    <h3>React Native</h3>
                    <p>Cross-platform mobile app</p>
                </div>
                <div class="tech-item">
                    <i class="fab fa-aws"></i>
                    <h3>AWS Infrastructure</h3>
                    <p>Auto-scaling cloud deployment</p>
                </div>
                <div class="tech-item">
                    <i class="fas fa-cube"></i>
                    <h3>Blockchain Security</h3>
                    <p>Document verification system</p>
                </div>
            </div>
        </div>
    </section>

    <section id="demo" class="demo-section">
        <div class="container">
            <h2 class="section-title">See Lawgic in Action</h2>
            <p style="font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto;">Watch how our AI transforms complex legal queries into simple, actionable insights in seconds.</p>
            
            <div class="demo-video">
                <div class="demo-placeholder">
                    <div class="play-button pulse">
                        <i class="fas fa-play"></i>
                    </div>
                    <h3>Product Demo Video</h3>
                    <p>Experience the future of legal assistance</p>
                    <p style="opacity: 0.7; font-size: 0.9rem;">Interactive demo showcasing multilingual AI, case prediction, and real-time document processing</p>
                </div>
            </div>
        </div>
    </section>

    <section id="investor" class="investor-cta">
        <div class="container">
            <div class="investor-content">
                <h2>Join India's Legal Revolution</h2>
                <p style="font-size: 1.3rem; margin-bottom: 2rem;">We're raising ₹50 Cr Series A to scale across India and capture the massive legal-tech opportunity.</p>
                
                <div class="investor-highlights">
                    <div class="highlight-item">
                        <div class="highlight-number">₹50 Cr</div>
                        <div>Series A Round</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-number">₹500 Cr</div>
                        <div>5-Year Revenue Target</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-number">50M+</div>
                        <div>Target Users by 2030</div>
                    </div>
                    <div class="highlight-item">
                        <div class="highlight-number">22</div>
                        <div>States Coverage</div>
                    </div>
                </div>

                <div class="cta-buttons">
                    <a href="mailto:investors@Lawgic.in" class="cta-button">
                        <i class="fas fa-envelope"></i> Get Pitch Deck
                    </a>
                    <a href="#contact" class="cta-button cta-secondary">
                        <i class="fas fa-calendar"></i> Schedule Meeting
                    </a>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <img src="logo.jpg" alt="Lawgic Logo" class="footer-logo">
                    <h3>Lawgic Platform</h3>
                    <p>Democratizing justice through AI innovation. Making legal services accessible, affordable, and efficient for every Indian citizen.</p>
                    <p style="margin-top: 1rem;"><strong>Backed by:</strong> Leading VCs and Legal Tech Accelerators</p>
                </div>
                <div class="footer-section">
                    <h3>Platform</h3>
                    <p><a href="#">AI Legal Assistant</a></p>
                    <p><a href="#">Case Prediction</a></p>
                    <p><a href="#">Document Processing</a></p>
                    <p><a href="#">Lawyer Network</a></p>
                    <p><a href="#">AI Arbitration</a></p>
                </div>
                <div class="footer-section">
                    <h3>Business</h3>
                    <p><a href="#">Revenue Model</a></p>
                    <p><a href="#">Partner Program</a></p>
                    <p><a href="#">Enterprise Solutions</a></p>
                    <p><a href="#">API Access</a></p>
                    <p><a href="#">White Label</a></p>
                </div>
                <div class="footer-section">
                    <h3>Investors</h3>
                    <p>Email: investors@Lawgic.in</p>
                    <p>Phone: +91 98765 43210</p>
                    <p>Address: Koramangala, Bangalore</p>
                    <p><a href="#">Download Pitch Deck</a></p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; <?php echo $current_year; ?> Lawgic. All rights reserved. Revolutionizing justice through AI technology.</p>
            </div>
        </div>
    </footer>

    <script>
        // Enhanced JavaScript with investor-focused interactions
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Animated counters for statistics
        function animateCounter(element, target, duration = 2000) {
            let start = 0;
            const increment = target / (duration / 16);
            
            function updateCounter() {
                start += increment;
                if (start < target) {
                    element.textContent = Math.floor(start).toLocaleString('en-IN');
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = target.toLocaleString('en-IN');
                }
            }
            updateCounter();
        }

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    
                    // Animate numbers when they come into view
                    const statNumbers = entry.target.querySelectorAll('.stat-number, .market-number');
                    statNumbers.forEach(stat => {
                        const value = parseInt(stat.textContent.replace(/[^\d]/g, ''));
                        if (value && !stat.hasAttribute('data-animated')) {
                            stat.setAttribute('data-animated', 'true');
                            animateCounter(stat, value);
                        }
                    });
                }
            });
        }, observerOptions);

        // Observe elements
        document.querySelectorAll('.fade-in, .market-opportunity, .hero-stats').forEach(el => {
            observer.observe(el);
        });

        // Dynamic hero background based on mouse movement
        const hero = document.querySelector('.hero');
        hero.addEventListener('mousemove', (e) => {
            const mouseX = (e.clientX / window.innerWidth) * 100;
            const mouseY = (e.clientY / window.innerHeight) * 100;
            
            hero.style.background = `
                radial-gradient(circle at ${mouseX}% ${mouseY}%, 
                rgba(59, 130, 246, 0.3) 0%, 
                transparent 50%),
                linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)
            `;
        });

        // Enhanced card hover effects
        document.querySelectorAll('.feature-card, .revenue-card, .advantage-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px) scale(1.02)';
                this.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.2)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '';
            });
        });

        // Demo video interaction
        document.querySelector('.demo-placeholder').addEventListener('click', function() {
            this.innerHTML = `
                <div style="padding: 4rem; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 2rem;">🚀</div>
                    <h3>Demo Coming Soon!</h3>
                    <p>Interactive product demo will be available in the full release.</p>
                    <p style="margin-top: 1rem; opacity: 0.8;">
                        <a href="mailto:demo@Lawgic.in" style="color: #fbbf24;">Request Early Access →</a>
                    </p>
                </div>
            `;
        });

        // Add typing effect to hero title
        const heroTitle = document.querySelector('.hero h1');
        const titleText = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let charIndex = 0;
        function typeWriter() {
            if (charIndex < titleText.length) {
                heroTitle.textContent += titleText.charAt(charIndex);
                charIndex++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Start typing effect after page load
        window.addEventListener('load', () => {
            setTimeout(typeWriter, 1000);
        });

        // Investor button special effects
        const investorButton = document.querySelector('.investor-button');
        investorButton.addEventListener('click', function(e) {
            // Add analytics tracking here
            console.log('Investor button clicked - track this conversion!');
        });

        // Add scroll progress indicator
        const scrollProgress = document.createElement('div');
        scrollProgress.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(45deg, #fbbf24, #f59e0b);
            z-index: 9999;
            transition: width 0.1s;
        `;
        document.body.appendChild(scrollProgress);

        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            scrollProgress.style.width = scrolled + '%';
        });

        // Logo animation on scroll
        const logoImage = document.querySelector('.logo-image');
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            logoImage.style.transform = `translateY(${rate}px)`;
        });
    </script>
</body>
</html>