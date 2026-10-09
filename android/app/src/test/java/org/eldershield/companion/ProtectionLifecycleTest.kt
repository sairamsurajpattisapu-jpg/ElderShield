package org.eldershield.companion

import org.eldershield.companion.data.ProtectionState
import org.eldershield.companion.service.ElderShieldProtectionService
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ProtectionLifecycleTest {

    @Test
    fun testProtectionStateTransitions() {
        val states = ProtectionState.values().map { it.name }
        assertTrue(states.contains("STOPPED"))
        assertTrue(states.contains("STARTING"))
        assertTrue(states.contains("CONNECTING"))
        assertTrue(states.contains("LIVE_PROTECTED"))
        assertTrue(states.contains("RECONNECTING"))
        assertTrue(states.contains("DEGRADED"))
        assertTrue(states.contains("FAILED"))
    }

    @Test
    fun testBoundedExponentialBackoff() {
        // Attempt 1: 1000ms
        assertEquals(1000L, ElderShieldProtectionService.calculateBackoffMs(1))
        // Attempt 2: 2000ms
        assertEquals(2000L, ElderShieldProtectionService.calculateBackoffMs(2))
        // Attempt 3: 4000ms
        assertEquals(4000L, ElderShieldProtectionService.calculateBackoffMs(3))
        // Attempt 4: 8000ms
        assertEquals(8000L, ElderShieldProtectionService.calculateBackoffMs(4))
        // Attempt 5: 16000ms
        assertEquals(16000L, ElderShieldProtectionService.calculateBackoffMs(5))
        // Attempt 6+: Bounded at 16000ms
        assertEquals(16000L, ElderShieldProtectionService.calculateBackoffMs(6))
        assertEquals(16000L, ElderShieldProtectionService.calculateBackoffMs(10))
    }

    @Test
    fun testAudioFormatParameters() {
        val sampleRate = 16000
        val bytesPerSample = 2 // 16-bit PCM
        val channels = 1 // Mono
        val bytesPerSecond = sampleRate * bytesPerSample * channels

        assertEquals(32000, bytesPerSecond)
        
        // 100ms audio frame byte length
        val expected100msBytes = bytesPerSecond / 10
        assertEquals(3200, expected100msBytes)

        // 2000ms accumulation buffer size (VAD window)
        val expected2000msBytes = bytesPerSecond * 2
        assertEquals(64000, expected2000msBytes)
    }

    @Test
    fun testMaxRetryAttemptsConstant() {
        assertEquals(5, ElderShieldProtectionService.MAX_RETRY_ATTEMPTS)
    }

    @Test
    fun testZeroAndNegativeAttemptBackoff() {
        // Defensive bounds: 0 or negative attempts should default to base 1000ms
        assertEquals(1000L, ElderShieldProtectionService.calculateBackoffMs(0))
        assertEquals(1000L, ElderShieldProtectionService.calculateBackoffMs(-1))
        assertEquals(1000L, ElderShieldProtectionService.calculateBackoffMs(-10))
    }

    @Test
    fun testServiceActionConstants() {
        assertEquals("org.eldershield.action.START_PROTECTION", ElderShieldProtectionService.ACTION_START)
        assertEquals("org.eldershield.action.STOP_PROTECTION", ElderShieldProtectionService.ACTION_STOP)
        assertEquals("org.eldershield.action.STATE_CHANGED", ElderShieldProtectionService.ACTION_STATE_CHANGED)
        assertEquals("org.eldershield.action.RISK_UPDATE", ElderShieldProtectionService.ACTION_RISK_UPDATE)
        assertEquals("org.eldershield.action.WARNING", ElderShieldProtectionService.ACTION_WARNING)
    }

    @Test
    fun testServerUrlValidation() {
        val (emptyValid, emptyErr) = org.eldershield.companion.data.PreferenceManager.validateServerUrl("")
        assertEquals(false, emptyValid)
        assertEquals("Server URL cannot be empty", emptyErr)

        val (validHttp, _) = org.eldershield.companion.data.PreferenceManager.validateServerUrl("http://192.168.1.50:8000")
        assertEquals(true, validHttp)

        val (validHttps, _) = org.eldershield.companion.data.PreferenceManager.validateServerUrl("https://api.eldershield.org")
        assertEquals(true, validHttps)

        val (validHostNoScheme, _) = org.eldershield.companion.data.PreferenceManager.validateServerUrl("10.0.2.2:8000")
        assertEquals(true, validHostNoScheme)
    }
}

