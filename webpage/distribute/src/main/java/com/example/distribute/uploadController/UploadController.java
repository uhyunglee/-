package com.example.distribute.uploadController;

import com.example.distribute.Configuration.*;
import org.springframework.core.io.Resource;
import com.example.distribute.storage.StorageException;
import com.example.distribute.storage.StorageFileNotFoundException;
import com.example.distribute.storage.StorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.web.servlet.view.RedirectView;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.MalformedURLException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.StringTokenizer;

import org.springframework.core.io.UrlResource;



@Controller
public class UploadController {
    private final Mode mode;
    private final StorageService storageService;
    private  String destinationFile = "";
    private String videoDistributeUrl = "http://192.168.0.11:30500";// "http://192.168.0.11:30500" ;//"http://localhost:5001"; // 5001로 변환해야함
    private String downloadPath;
    private final ConversionService conversionService;
    private Progress[] progressList;
    private float threshold;


    @Autowired
    public UploadController(Mode mode, StorageService storageService, ConversionService conversionService, Progress[] PropresetList) {
        this.mode = mode;
        this.storageService = storageService;
        this.conversionService = conversionService;
        this.progressList = PropresetList;
    }

    @RequestMapping(value = "/", method =  RequestMethod.GET)
    public String upload(Model model){
        conversionService.setConversionStatus("ready");
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
    public String handleFileUpload(@RequestParam("file") MultipartFile file ,@RequestParam("threshold") String threshold ) {
        this.threshold = Float.parseFloat(threshold);
        storageService.store(file);
        destinationFile = storageService.store(file);

        return "redirect:/mode/file/videoinformation";
    }

    @GetMapping("mode/file/videoinformation")
    public String showVideoInformation(Model model, RestTemplate restTemplate)throws  Exception{
        model.addAttribute("mode",mode.getMode());
        model.addAttribute("filePath", destinationFile);
        System.out.println(destinationFile);
        System.out.println(this.threshold);
        UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(videoDistributeUrl+"/videoinformation").queryParam("mode", mode.getMode()).queryParam("filepath", destinationFile).queryParam("threshold",this.threshold);
        String url = builder.toUriString();
        System.out.print(url);
        videoInformation videoinformation = restTemplate.getForObject(url, com.example.distribute.Configuration.videoInformation.class);

        model.addAttribute("frameWidth", videoinformation.frameWidth());
        model.addAttribute("frameHeight", videoinformation.frameHeight());
        model.addAttribute("frameCount", videoinformation.frameCount());
        model.addAttribute("fps", videoinformation.fps());
        model.addAttribute("videoLength", videoinformation.videoLength());
        model.addAttribute("nodeCount",videoinformation.nodeCount());

        initProgressList(videoinformation.nodeCount());
//        initProgressList(3);
//        model.addAttribute("nodeCount",3);

        return "videoinformation";
    }

    @GetMapping("mode/file/download")
    public String showDownLoadPage(Model model , RestTemplate restTemplate){
        System.out.println("show DownLoadPage");
        downloadInformation downloadinformation = restTemplate.getForObject(videoDistributeUrl+"/download", com.example.distribute.Configuration.downloadInformation.class);
        System.out.println("1");
        model.addAttribute("mode", mode.getMode());
        System.out.println("2");
        model.addAttribute("waitTime", downloadinformation.waitTime());
        model.addAttribute("dropCount",downloadinformation.dropCount());
        System.out.println(downloadinformation.waitTime());
        System.out.println(downloadinformation.dropCount());
        downloadPath  = downloadinformation.downloadPath();
        System.out.println(downloadPath);

//        downloadPath = "D:\\Capstone\\yolo5_light_file_size\\data\\video\\traffic-mini.mp4";

        return "download";
    }

    @PostMapping("/api/videoUrl")
    public ResponseEntity<?> videoUrl() throws  Exception{
        HashMap<String, String> videoUrl = new HashMap<>();
        videoUrl.put("url", "D:\\Capstone\\yolo5_light_file_size\\data\\video\\traffic-mini.mp4");

        return new ResponseEntity<HashMap<String, String>>(videoUrl, HttpStatus.OK);
    }

    @GetMapping("mode/file/download/final")
    public ResponseEntity<Resource> downloadFile() {
       // downloadPath = "D:\\Capstone\\yolo5_light_file_size\\data\\video\\traffic-mini.mp4"; // 다운로드할 파일의 경로

        try {
            Path file = Paths.get(downloadPath);
            Resource resource = new UrlResource(file.toUri());

            if (resource.exists()) {
                return ResponseEntity.ok()
                        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                        .contentType(MediaType.APPLICATION_OCTET_STREAM)
                        .body(resource);
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }

        // 다운로드할 파일이 존재하지 않을 경우에 대한 처리
        return ResponseEntity.notFound().build();
    }

    @GetMapping("/mode/file/progress/{progressBarId}")
    @ResponseBody
    public String updateProgress(@PathVariable("progressBarId") String progressBarId) {
        int id = Integer.parseInt(progressBarId);
        String strPersent = Integer.toString(progressList[id].getPersent());
        return "{\"progressBarId\": \"" + progressBarId + "\", \"progress\": " + strPersent + "}";
    }

    @PostMapping("/progress/{progressBarId}/{persent}")
    public ResponseEntity<Integer> setProgresss(@PathVariable("progressBarId") int progressBarId, @PathVariable("persent") int persent){
        progressList[progressBarId].setPersent(persent);
        return ResponseEntity.ok(200);
    }

    @GetMapping("/nodecount")
    public ResponseEntity<Integer> returnNodeCount(){
        return ResponseEntity.ok(progressList.length -1);
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

    protected void initProgressList(int nodeCount){
        this.progressList = new Progress[nodeCount+1];
        for(int i = 1; i<=nodeCount; i++){
            progressList[i] = new Progress();
            progressList[i].setPersent(0);
        }
        for(int i =1; i<nodeCount; i++){
            System.out.println(progressList[i].getPersent());
        }
    }

}
