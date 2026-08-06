package com.naturaai.service;

import com.naturaai.dto.AnalyzeRequest;
import com.naturaai.dto.AnalyzeResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

@Component
public class MlEngineClient {

    private static final Logger log = LoggerFactory.getLogger(MlEngineClient.class);

    private final RestClient restClient;

    public MlEngineClient(
            RestClient.Builder builder,
            @Value("${naturaai.ml-engine-url}") String mlEngineUrl) {
        HttpClient httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        ClientHttpRequestFactory requestFactory = new JdkClientHttpRequestFactory(httpClient);

        this.restClient = builder
                .baseUrl(mlEngineUrl)
                .requestFactory(requestFactory)
                .requestInterceptor((request, body, execution) -> {
                    if (log.isDebugEnabled()) {
                        log.debug("{} {} body={}",
                                request.getMethod(), request.getURI(),
                                new String(body, StandardCharsets.UTF_8));
                    }
                    return execution.execute(request, body);
                })
                .build();
    }

    public AnalyzeResponse predict(AnalyzeRequest request) {
        return restClient.post()
                .uri("/predict")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(AnalyzeResponse.class);
    }
}
