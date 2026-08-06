package com.naturaai.controller;

import com.naturaai.model.Herb;
import com.naturaai.service.HerbService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/api/v1/herbs")
public class HerbController {

    private final HerbService herbService;

    public HerbController(HerbService herbService) {
        this.herbService = herbService;
    }

    @GetMapping
    public List<Herb> all() {
        return herbService.findAll();
    }

    @GetMapping("/search")
    public List<Herb> search(@RequestParam String q) {
        return herbService.search(q);
    }

    @GetMapping("/{name}")
    public Herb byName(@PathVariable String name) {
        Herb herb = herbService.findByName(name);
        if (herb == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Herb not found: " + name);
        }
        return herb;
    }
}
