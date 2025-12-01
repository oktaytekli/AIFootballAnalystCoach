console.log("Script.js v4.0 (Full Feature) yüklendi.");

document.addEventListener('DOMContentLoaded', () => {
    
    //GLOBAL DEĞİŞKENLER
    let activeTeam = 1; 
    let team1Color = null; // [R, G, B]
    let team2Color = null; // [R, G, B]
    let intervalId = null; // Canlı veri çekme döngüsü için
    
    //Global veri saklama (Window altında tutuyoruz)
    window.setupData = {}; 

    // BÖLÜM 1: ANASAYFA VE ARAYÜZ EFEKTLERİ
    
    //Anasayfa Animasyonları (Landing Page)
    const typewriterElement = document.getElementById('typewriter');
    if (typewriterElement) {
        if (typeof AOS !== 'undefined') AOS.init({ duration: 1000, once: true });
        if (typeof Typed !== 'undefined') {
            new Typed('#typewriter', {
                strings: ['Yapay Zeka İle Çözün.', 'Veriye Dönüştürün.', 'Geleceğe Taşıyın.'],
                typeSpeed: 50, backSpeed: 30, backDelay: 2000, loop: true
            });
        }
    }

    //Dashboard Sidebar (Aç/Kapa)
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        window.toggleSidebar = function() {
            const menuTexts = document.querySelectorAll('.menu-text');
            const isExpanded = sidebar.classList.contains('w-64');

            if (isExpanded) {
                sidebar.classList.remove('w-64');
                sidebar.classList.add('w-20');
                menuTexts.forEach(text => text.classList.add('hidden'));
            } else {
                sidebar.classList.remove('w-20');
                sidebar.classList.add('w-64');
                setTimeout(() => {
                    menuTexts.forEach(text => text.classList.remove('hidden'));
                }, 100);
            }
        };
    }

    // BÖLÜM 2: ANALİZ KURULUM SİHİRBAZI (WIZARD)
    
    //Sihirbazı Aç
    window.openWizard = function() {
        const url = document.getElementById('mainVideoUrl').value;
        if (!url) return alert("Lütfen önce bir YouTube linki yapıştırın!");

        document.getElementById('setupModal').classList.add('active');
        
        //Arayüzü Sıfırla
        document.getElementById('step1').classList.remove('hidden');
        document.getElementById('step2').classList.add('hidden');
        document.getElementById('placeholderImg').style.display = 'block';
        document.getElementById('previewImage').style.display = 'none';
        document.getElementById('loadingImg').style.display = 'none';
    };

    //Sihirbazı Kapat
    window.closeModal = function() {
        document.getElementById('setupModal').classList.remove('active');
    };

    //Backend'den Kare İste (Snapshot)
    window.getSnapshot = async function() {
        const url = document.getElementById('mainVideoUrl').value;
        const min = document.getElementById('snapshotMin').value || 2;

        //UI Durumu
        document.getElementById('placeholderImg').style.display = 'none';
        document.getElementById('previewImage').style.display = 'none';
        document.getElementById('loadingImg').style.display = 'block';

        try {
            const res = await fetch('/get_frame', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url, time_min: min })
            });
            const data = await res.json();
            
            if(data.status === 'ok') {
                const img = document.getElementById('previewImage');
                img.src = "data:image/jpeg;base64," + data.image;
                img.style.display = 'block';
                document.getElementById('loadingImg').style.display = 'none';
            } else {
                alert("Görüntü alınamadı. Linki veya dakikayı kontrol edin.");
                document.getElementById('loadingImg').style.display = 'none';
                document.getElementById('placeholderImg').style.display = 'block';
            }
        } catch(e) {
            console.error(e);
            alert("Sunucu hatası!");
        }
    };

    // BÖLÜM 3: RENK SEÇİMİ VE TAKIM AYARLARI

    //Hangi takımın rengini seçiyoruz?
    window.selectActiveTeam = function(teamId) {
        activeTeam = teamId;
        //Görsel seçim efekti (Yeşil çerçeve)
        document.getElementById('cardTeam1').style.borderColor = (teamId===1) ? '#4ade80' : '#334155';
        document.getElementById('cardTeam2').style.borderColor = (teamId===2) ? '#4ade80' : '#334155';
    };

    //RGB'den HEX Kodu Çevirici
    function rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
    }

    //Fotoğrafa Tıklayınca Rengi Al
    window.pickColor = function(event) {
        const img = document.getElementById('previewImage');
        const canvas = document.getElementById('colorCanvas');
        
        if (!canvas) return; //Hata önleyici
        
        const ctx = canvas.getContext('2d');

        //Resmi canvas'a çiz
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);

        //Tıklanan koordinatı hesapla (Responsive düzeltme)
        const rect = img.getBoundingClientRect();
        const x = Math.floor((event.clientX - rect.left) * (img.naturalWidth / rect.width));
        const y = Math.floor((event.clientY - rect.top) * (img.naturalHeight / rect.height));

        //Piksel verisini al [R, G, B, A]
        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const rgbColor = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;
        const hexColor = rgbToHex(pixel[0], pixel[1], pixel[2]);

        //Kutuyu boya ve kodu yaz
        document.getElementById(`colorBox${activeTeam}`).style.backgroundColor = rgbColor;
        document.getElementById(`colorCode${activeTeam}`).innerText = hexColor;

        //Backend'e göndermek üzere kaydet
        if(activeTeam === 1) team1Color = [pixel[0], pixel[1], pixel[2]];
        if(activeTeam === 2) team2Color = [pixel[0], pixel[1], pixel[2]];
    };

    // BÖLÜM 4: TOKEN VE BAKİYE HESAPLAMA
    //Adım 2'ye Geç
    window.goToStep2 = async function() {
        document.getElementById('step1').classList.add('hidden');
        document.getElementById('step2').classList.remove('hidden');
        await calculateCost(); //Fiyatı anında hesapla
    };

    window.backToStep1 = function() {
        document.getElementById('step2').classList.add('hidden');
        document.getElementById('step1').classList.remove('hidden');
    };

    //Maliyet Hesapla
    async function calculateCost() {
        const start = parseInt(document.getElementById('startMin').value);
        const end = parseInt(document.getElementById('endMin').value);
        
        const res = await fetch('/calculate_cost', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({start: start, end: end})
        });
        const data = await res.json();
        
        document.getElementById('costVal').innerText = data.cost;
        document.getElementById('balanceVal').innerText = data.balance;
        
        const btnPay = document.getElementById('btnPay');
        const btnUseBal = document.getElementById('btnUseBalance');
        const warning = document.getElementById('balanceWarning');
        
        //BAKİYE KONTROL MANTIĞI
        if (data.can_afford) {
            //Para yetiyor
            btnPay.disabled = false;
            btnPay.classList.remove('opacity-50', 'cursor-not-allowed');
            btnPay.innerText = "Öde ve Başlat";
            btnUseBal.classList.add('hidden');
            if(warning) warning.classList.add('hidden');
        } else {
            //Para yetmiyor
            btnPay.disabled = true;
            btnPay.classList.add('opacity-50', 'cursor-not-allowed');
            btnPay.innerText = "Yetersiz Bakiye";
            if(warning) warning.classList.remove('hidden');
            
            //"Bakiyem kadar oynat" seçeneği sun
            if(data.balance > 0) {
                btnUseBal.classList.remove('hidden');
                document.getElementById('maxTimeVal').innerText = data.max_minutes;
                window.setupData.maxDuration = data.max_minutes;
            }
        }
    }

    // BÖLÜM 5: ANALİZ BAŞLATMA

    //1.Seçenek: Tam süreyi öde ve başlat
    window.confirmStart = async function() {
        const duration = document.getElementById('endMin').value - document.getElementById('startMin').value;
        await startAnalysisRequest(duration);
    };

    //2.Seçenek: Bakiyem kadarını başlat
    window.useMaxBalance = async function() {
        await startAnalysisRequest(window.setupData.maxDuration);
    };

    //Backend'e başlatma isteği gönderen ana fonksiyon
    async function startAnalysisRequest(duration) {
        //İsimleri al
        const t1Name = document.getElementById('wizTeam1Name').value;
        const t2Name = document.getElementById('wizTeam2Name').value;
        const videoUrl = document.getElementById('mainVideoUrl').value;

        const payload = {
            video_url: videoUrl, //URL'i backend'e gönderiyoruz
            t1_name: t1Name,
            t2_name: t2Name,
            t1_rgb: team1Color, 
            t2_rgb: team2Color,
            start_min: document.getElementById('startMin').value,
            duration: duration,
            cost: duration 
        };

        const res = await fetch('/start_session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if(res.ok) {
            closeModal(); // Pencreyi kapat
            
            //Arayüzü Hazırla ve Videoyu Başlat
            const startSec = payload.start_min * 60;
            const videoImg = document.getElementById('videoFeed');
            
            //Cache önlemek için timestamp ekliyoruz
            videoImg.src = `/video_feed?url=${encodeURIComponent(videoUrl)}&start=${startSec}&t=${new Date().getTime()}`;
            
            videoImg.classList.remove('hidden');
            document.getElementById('videoPlaceholder').classList.add('hidden');
            
            //Dashboard İsimlerini Güncelle
            document.getElementById('lblTeam1').innerText = t1Name;
            document.getElementById('lblTeam2').innerText = t2Name;
            
            //Bakiyeyi güncelle (Sidebar)
            updateSidebarBalance();

            //Veri Çekme Döngüsünü Başlat
            if (intervalId) clearInterval(intervalId);
            intervalId = setInterval(fetchLiveStats, 1000); 
        } else {
            const err = await res.json();
            alert("Hata: " + (err.message || "Analiz başlatılamadı"));
        }
    }
    
    // BÖLÜM 6: DASHBOARD KONTROLLERİ

    //Analizi Durdur
    window.stopAnalysis = async function() {
        if(!confirm("Analizi bitirmek istediğinize emin misiniz?")) return;
        
        await fetch('/stop_analysis', {method: 'POST'});
        if (intervalId) clearInterval(intervalId);
        location.reload(); 
    };

    //Video Kontrolleri (Play/Pause/Seek)
    window.controlVideo = async function(action) {
        const btnPlay = document.getElementById('btn-play');
        const btnPause = document.getElementById('btn-pause');

        if (action === 'pause') {
            btnPause.classList.add('hidden');
            btnPlay.classList.remove('hidden');
        } else if (action === 'play') {
            btnPlay.classList.add('hidden');
            btnPause.classList.remove('hidden');
        }

        try {
            await fetch('/control_video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: action })
            });
        } catch (error) { console.error(error); }
    };

    //Takım İsimlerini Manuel Güncelleme (Dashboard içinden)
    window.updateTeamNames = async function() {
        const t1 = document.getElementById('inputTeam1').value || "Takım A";
        const t2 = document.getElementById('inputTeam2').value || "Takım B";

        document.getElementById('labelTeam1').innerText = t1;
        document.getElementById('labelTeam2').innerText = t2;

        await fetch('/update_teams', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ team1: t1, team2: t2 })
        });
    };
    // BÖLÜM 7: VERİ AKIŞI

    //Sidebar Bakiye Güncelleyici
    async function updateSidebarBalance() {
        try {
            const res = await fetch('/get_balance');
            const data = await res.json();
            const el = document.getElementById('sidebarBalance');
            if(el) el.innerText = data.balance;
        } catch(e) {}
    }
    //Sayfa açılınca ve her 10 saniyede bir kontrol et
    if(document.getElementById('sidebarBalance')) {
        updateSidebarBalance();
        setInterval(updateSidebarBalance, 10000);
    }

    //Canlı İstatistik Çekme
    async function fetchLiveStats() {
        try {
            const res = await fetch('/data');
            if(!res.ok) return;

            const data = await res.json();

            //Skorlar
            document.getElementById('team1-count').innerText = data.team1;
            document.getElementById('team2-count').innerText = data.team2;
            document.getElementById('coach-comment').innerText = data.comment;

            //Barlar
            const total = data.team1 + data.team2 + 0.01;
            document.getElementById('bar1').style.width = (data.team1 / total * 100) + "%";
            document.getElementById('bar2').style.width = (data.team2 / total * 100) + "%";

            //Top Durumu
            const ballStatus = document.getElementById('ball-status');
            if(ballStatus) {
                ballStatus.innerText = data.ball ? "GÖRÜNDÜ" : "KAYIP";
                ballStatus.className = data.ball 
                    ? "px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-bold border border-green-500/30"
                    : "px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-bold border border-red-500/30";
            }

        } catch (error) { console.error("Veri hatası", error); }
    }
});