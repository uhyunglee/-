package com.example.distribute.uploadController;

import com.example.distribute.Configuration.Mode;
import com.example.distribute.Configuration.videoInformation;
import com.example.distribute.storage.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.web.servlet.view.RedirectView;

@Controller
public class UploadController {
    private final Mode mode;
    private final StorageService storageService;
    private  String destinationFile;
    private String videoDistributeUrl = "http://localhost:5001";

    @Autowired
    public UploadController(Mode mode, StorageService storageService) {
        this.mode = mode;
        this.storageService = storageService;
    }

    @RequestMapping(value = "/", method =  RequestMethod.GET)
    public String upload(Model model){
        model.addAttribute("mode", new Mode());

        return "mode";
    }

    @RequestMapping(value="/mode", method = RequestMethod.POST)
    public String selected(Model model, Mode mode){
        this.mode.setMode(mode.getMode());
        model.addAttribute("mode", mode.getMode());
        return "file";
    }

    @GetMapping("/mode/file")
    public String uploadFile(Model model){
        return isModeNUll("file");
    }

    @PostMapping("/mode/file")
    public String handleFileUpload(@RequestParam("file") MultipartFile file) {
        destinationFile = storageService.store(file);

        return "redirect:/mode/file/videoinformation";
    }

    @GetMapping("mode/file/videoinformation")
    public String showVideoInformation(Model model, RestTemplate restTemplate)throws  Exception{
        model.addAttribute("mode",mode.getMode());
        model.addAttribute("filePath", destinationFile);

        videoInformation videoinformation = restTemplate.getForObject(videoDistributeUrl+"/videoinformation", com.example.distribute.Configuration.videoInformation.class);
        model.addAttribute("frameWeight",videoinformation.frameWeight());
        model.addAttribute("frameHeight",videoinformation.frameHeight());
        model.addAttribute("frameCount",videoinformation.frameCount());
        model.addAttribute("fps",videoinformation.fps());
        model.addAttribute("videoLength",videoinformation.videoLength());


        return "videoinformation";
    }



    @ExceptionHandler(StorageFileNotFoundException.class)
    public ResponseEntity<?> handleStorageFileNotFound(StorageFileNotFoundException exc) {
        return ResponseEntity.notFound().build();
    }
    @ExceptionHandler(StorageException.class)
    public RedirectView handleStorageException(StorageException e ,RedirectAttributes rttr) {
        String redirect = "/mode/file";
        RedirectView rw = new RedirectView(redirect);
        rttr.addFlashAttribute("storageExceptionMessage",e.getMessage());
        rttr.addFlashAttribute("mode", mode.getMode());

        return rw;
    }

    public String isModeNUll(String nowPage){
        if(mode.getMode().equals("")){
            return "redirect:/";
        }
        return nowPage;
    }


}
