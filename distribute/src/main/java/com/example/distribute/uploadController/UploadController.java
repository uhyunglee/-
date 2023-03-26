package com.example.distribute.uploadController;

import com.example.distribute.Configuration.Mode;
import com.example.distribute.storage.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.web.servlet.view.RedirectView;

@Controller
public class UploadController {
    private final Mode mode;
    private final StorageService storageService;

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
        return "file";
    }

    @PostMapping("/mode/file")
    public String handleFileUpload(@RequestParam("file") MultipartFile file) {
        storageService.store(file);
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

        //rttr.addFlashAttribute("mode");
        //System.out.println(mode.getMode());

//        FlashMap outputFlashMap = RequestContextUtils.getOutputFlashMap(request);
//        if (outputFlashMap != null){
//            outputFlashMap.put("storageExceptionMessage",e);
//        }

        return rw;
    }


}
