package com.pelita.terakhir;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Membungkus permainan yang sama dengan versi web: server Flask berjalan di dalam
 * aplikasi ini (Python lewat Chaquopy), dan WebView menampilkannya dari 127.0.0.1.
 *
 * Tidak ada lalu lintas keluar perangkat. Soket hanya mendengar di loopback.
 */
public class MainActivity extends Activity {

    private static final String HOST = "127.0.0.1";
    private static final int TUNGGU_SERVER_MS = 40_000;

    private WebView web;
    private View splash;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private long terakhirTekanKembali = 0;
    private boolean sudahDimuat = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        web = findViewById(R.id.web);
        splash = findViewById(R.id.splash);
        siapkanWebView();
        new Thread(this::jalankanServer, "pelita-server").start();
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void siapkanWebView() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);          // seluruh antarmuka permainan adalah JS
        s.setDomStorageEnabled(true);
        s.setSupportZoom(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            s.setSafeBrowsingEnabled(false);   // isi halaman berasal dari aplikasi ini sendiri
        }
        web.setBackgroundColor(0xFF0C0F14);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                // Kunci navigasi ke server lokal; tidak ada tautan keluar di permainan.
                return !HOST.equals(r.getUrl().getHost());
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                if (!sudahDimuat) {
                    sudahDimuat = true;
                    splash.setVisibility(View.GONE);
                    web.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                if (r.isForMainFrame()) {
                    tampilkanGagal(getString(R.string.gagal));
                }
            }
        });
    }

    /** Mulai Python, jalankan Flask di porta bebas, lalu arahkan WebView ke sana. */
    private void jalankanServer() {
        try {
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(this));
            }
            int port = portBebas();
            String simpanan = getFilesDir().getAbsolutePath() + "/saves";

            PyObject modul = Python.getInstance().getModule("pelita_android");
            new Thread(() -> modul.callAttr("jalankan_server", HOST, port, simpanan),
                       "pelita-flask").start();

            if (!tungguPortTerbuka(port, TUNGGU_SERVER_MS)) {
                ui.post(() -> tampilkanGagal(getString(R.string.gagal)));
                return;
            }
            String url = "http://" + HOST + ":" + port + "/";
            ui.post(() -> web.loadUrl(url));
        } catch (Throwable t) {
            ui.post(() -> tampilkanGagal(t.getClass().getSimpleName() + ": " + t.getMessage()));
        }
    }

    /** Porta yang sedang bebas. Dilepas lagi supaya Python bisa memakainya. */
    private static int portBebas() throws IOException {
        try (ServerSocket s = new ServerSocket(0)) {
            s.setReuseAddress(true);
            return s.getLocalPort();
        }
    }

    private static boolean tungguPortTerbuka(int port, int batasMs) {
        long batas = System.currentTimeMillis() + batasMs;
        while (System.currentTimeMillis() < batas) {
            try (Socket s = new Socket()) {
                s.connect(new InetSocketAddress(HOST, port), 400);
                return true;
            } catch (IOException ignored) {
                try {
                    Thread.sleep(150);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
        }
        return false;
    }

    private void tampilkanGagal(String pesan) {
        TextView judul = findViewById(R.id.splash_judul);
        TextView detail = findViewById(R.id.splash_pesan);
        judul.setText(R.string.gagal);
        detail.setText(pesan);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            // Permainan tidak memakai riwayat halaman, jadi Back dipakai untuk keluar,
            // dengan konfirmasi supaya tidak tertekan tak sengaja saat bertarung.
            long now = System.currentTimeMillis();
            if (now - terakhirTekanKembali < 2000) {
                finish();
            } else {
                terakhirTekanKembali = now;
                Toast.makeText(this, R.string.tekan_lagi, Toast.LENGTH_SHORT).show();
            }
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
