package com.naturaai.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

@Service
public class MailService {

    private static final Logger log = LoggerFactory.getLogger(MailService.class);

    private final JavaMailSender mailSender;
    private final String smtpHost;
    private final String from;

    public MailService(
            ObjectProvider<JavaMailSender> mailSenderProvider,
            @Value("${spring.mail.host:}") String smtpHost,
            @Value("${naturaai.mail.from:no-reply@naturaai.com}") String from) {
        this.mailSender = mailSenderProvider.getIfAvailable();
        this.smtpHost = smtpHost;
        this.from = from;
    }

    private boolean smtpConfigured() {
        return smtpHost != null && !smtpHost.isBlank();
    }

    @Async
    public void sendVerificationEmail(String to, String name, String verificationUrl) {
        send(to, "Verify your NaturaAI account",
                "Hi " + name + ",\n\n"
                        + "Welcome to NaturaAI! Please verify your email address by clicking the link below:\n\n"
                        + verificationUrl + "\n\n"
                        + "This link expires in 1 hour. If you didn't create an account, you can safely ignore this email.\n\n"
                        + "— The NaturaAI Team");
    }

    @Async
    public void sendLoginNotificationEmail(String to, String name) {
        send(to, "New sign-in to your NaturaAI account",
                "Hi " + name + ",\n\n"
                        + "A new sign-in to your NaturaAI account was just made. If this was you, no action is needed.\n\n"
                        + "If you didn't sign in, please reset your password immediately.\n\n"
                        + "— The NaturaAI Team");
    }

    @Async
    public void sendPasswordResetEmail(String to, String name, String resetUrl) {
        send(to, "Reset your NaturaAI password",
                "Hi " + name + ",\n\n"
                        + "We received a request to reset your NaturaAI account password. "
                        + "Click the link below to choose a new password:\n\n"
                        + resetUrl + "\n\n"
                        + "This link expires in 30 minutes. If you didn't request this, "
                        + "you can safely ignore this email.\n\n"
                        + "— The NaturaAI Team");
    }

    private void send(String to, String subject, String body) {
        if (smtpConfigured() && mailSender != null) {
            try {
                SimpleMailMessage message = new SimpleMailMessage();
                message.setFrom(from);
                message.setTo(to);
                message.setSubject(subject);
                message.setText(body);
                mailSender.send(message);
                log.info("Email sent to {}", to);
            } catch (Exception ex) {
                log.error("Failed to send email to {}: {}", to, ex.getMessage(), ex);
            }
        } else {
            log.warn("\n=======================================================\n"
                            + "EMAIL (DEV MODE - SMTP not configured)\n"
                            + "To: {}\nSubject: {}\n{}\n"
                            + "=======================================================\n",
                    to, subject, body);
        }
    }
}
