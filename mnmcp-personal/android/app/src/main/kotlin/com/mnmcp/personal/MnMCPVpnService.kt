package com.mnmcp.personal

import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import java.io.FileInputStream
import java.io.FileOutputStream

/**
 * MnMCP VPN Service
 * 捕获迷你世界网络流量并转发到 MnMCP 代理
 */
class MnMCPVpnService : VpnService() {
    private var vpnInterface: ParcelFileDescriptor? = null
    private var isRunning = false

    companion object {
        const val ACTION_START = "com.mnmcp.personal.VPN_START"
        const val ACTION_STOP = "com.mnmcp.personal.VPN_STOP"

        // 迷你世界云服 IP (从 mnmcp-core 配置同步)
        val MNW_CLOUD_IPS = listOf(
            "183.60.230.67",
            "183.36.42.103",
            "120.236.197.36",
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startVpn()
            ACTION_STOP -> stopVpn()
        }
        return START_STICKY
    }

    private fun startVpn() {
        if (isRunning) return

        vpnInterface = Builder()
            .setSession("MnMCP")
            .addAddress("10.8.0.1", 24)
            .apply {
                // 只路由迷你世界云服流量
                MNW_CLOUD_IPS.forEach { ip ->
                    addRoute(ip, 32)
                }
            }
            .establish()

        isRunning = true
        // TODO: 启动数据包转发线程
    }

    private fun stopVpn() {
        isRunning = false
        vpnInterface?.close()
        vpnInterface = null
        stopSelf()
    }

    override fun onDestroy() {
        stopVpn()
        super.onDestroy()
    }
}
